from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub
from langchain_community.tools import YouTubeSearchTool
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_google_genai import GoogleGenerativeAI
from langchain.embeddings import SentenceTransformerEmbeddings
# Initialize the Flask application
app = Flask(__name__)

# Initialize the movie chatbot components
api_key = 'AIzaSyDg23ttajQ6Of7btE9av1YwfSY3w7Seq9Q'
llm = GoogleGenerativeAI(model="models/gemini-pro", google_api_key=api_key)
prompt = PromptTemplate(
    template="""
    You are a movie expert. You find movies from a genre or plot.

    Chat History:{chat_history}
    Question:{input}
    """,
    input_variables=["chat_history", "input"],
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

chat_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

youtube = YouTubeSearchTool()
embeddings = SentenceTransformerEmbeddings(model_name='sentence-transformers/bert-large-nli-mean-tokens')
movie_plot_vector = Neo4jVector.from_existing_index(
    embeddings,
    url="bolt://localhost:7687",
    username="neo4j",
    password="kallind123",
    index_name="moviePlots",
    embedding_node_property="embedding",
    text_node_property="plot",
)

plot_retriever = RetrievalQA.from_llm(
    llm=llm,
    retriever=movie_plot_vector.as_retriever(),
    verbose=True,
    return_source_documents=True
)

def run_retriever(query):
    results = plot_retriever.invoke({"query":query})
    # format the results
    movies = '\n'.join([doc.metadata["title"] + " - " + doc.page_content for doc in results["source_documents"]])
    return movies

tools = [
    Tool.from_function(
        name="Movie Chat",
        description="For when you need to chat about movies. The question will be a string. Return a string.",
        func=chat_chain.run,
        return_direct=True,
    ),
    Tool.from_function(
        name="Movie Trailer Search",
        description="Use when needing to find a movie trailer. The question will include the word 'trailer'. Return a link to a YouTube video.",
        func=youtube.run,
        return_direct=True,
    ),
    Tool.from_function(
        name="Movie Plot Search",
        description="For when you need to compare a plot to a movie. The question will be a string. Return a string.",
        func=run_retriever,
        return_direct=True
    )
]

agent_prompt = hub.pull("hwchase17/react-chat")
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    max_interations=3,
    verbose=True,
    handle_parse_errors=True,
)

# Define the route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Define the route for handling chat messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    response = agent_executor.invoke({"input": user_message})
    return jsonify({"response": response["output"]})

if __name__ == '__main__':
    app.run(debug=True, port= 5001)
