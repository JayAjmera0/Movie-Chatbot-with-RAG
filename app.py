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
from langchain_community.embeddings import SentenceTransformerEmbeddings
from neo4j import GraphDatabase

# Initialize the Flask application
app = Flask(__name__)

# Initialize the movie chatbot components
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
embeddings = SentenceTransformerEmbeddings(model_name='intfloat/e5-large-v2')

movie_plot_vector = Neo4jVector.from_existing_index(
    embeddings,
    url="bolt://localhost:7687",
    username="neo4j",
    password= "password",
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
    results = plot_retriever.invoke({"query": query})
    # format the results
    movies = '\n'.join([doc.metadata["title"] + " - " + doc.page_content for doc in results["source_documents"]])
    return movies

uri = "bolt://localhost:7687"
username = "neo4j"
password = "kallind123"

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

def fetch_neo(tx, query):
    result = tx.run(query)
    records = list(result)
    data = [record.data() for record in records]
    return data

answer_misc = PromptTemplate(
    template="""The Labels of my neo4j database are:
    Actor, Director, Genre, Movie, Person, User.

    These are the properties that can be in these labels:
    bio, born, bornIn, budget, countries, died, embedding, imdbId, imdbRating, imdbVotes, languages, movieId, name, plot, poster, rating, released, revenue, role, runtime, tagline, timestamp, title, tmdbId, URL, userId, year.

    These are the relationships between Nodes.
    ACTED_IN
    DIRECTED
    IN_GENRE
    RATED

    Remember: 
    Always add a WHERE clause to your query to filter the results from null values.
    Return ONLY the Cypher Query to fetch the answer to the following question in this format
    cypher: query. No explanation, no extra stuff, return only the Cypher query:
    {question}""",
    input_variables=["question"],
)

def run_misc(query):
    answer = llm.invoke(answer_misc.format(question=query))
    # Trim the string to eliminate the first 6 characters
    print("Original Answer:", answer)
    cypher_query = str(answer[7:])
    print("Trimmed Cypher Query:", cypher_query)
    print("Type of Trimmed Query:", type(cypher_query))

    with driver.session() as session:
        result = session.read_transaction(fetch_neo, cypher_query)

    # Process the result to create a string output
    result_data = [record for record in result]
    formatted_result = '\n'.join([str(record) for record in result_data])
    print("Formatted Result:", formatted_result)

    return formatted_result

tools = [
    Tool.from_function(
        name="Movie Chat",
        description="For when you need to chat about finding movies. The question will be a string. Return a string.",
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
    ),
    Tool.from_function(
        name="Miscellaneous",
        description="For when you need to answer a miscellaneous question regarding information about movies, actors, directors, etc. The question will be a string. Return a string.",
        func=run_misc,
        return_direct=True
    ),
]

agent_prompt = hub.pull("hwchase17/react-chat")
agent_prompt.template += "It is compulsory for you to use a tool to answer the question."
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
    app.run(debug=True, port=5001)
