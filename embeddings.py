from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

# Load the pre-trained model for generating embeddings
model = SentenceTransformer('intfloat/e5-large-v2')

# Define Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "kallind123"

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

def fetch_movie_nodes(tx):
    query = """
    MATCH (m:Movie)
    RETURN id(m) as node_id, m.title as title, m.plot as plot
    """
    result = tx.run(query)
    return [{"node_id": record["node_id"], "title": record["title"], "plot": record["plot"]} for record in result]

def update_node_with_embedding(tx, node_id, embedding):
    query = """
    MATCH (m:Movie)
    WHERE id(m) = $node_id
    SET m.embedding = $embedding
    """
    tx.run(query, node_id=node_id, embedding=embedding.tolist())

# Fetch all Movie nodes and generate embeddings
with driver.session() as session:
    movie_nodes = session.read_transaction(fetch_movie_nodes)
    
    for node in movie_nodes:
        title = node["title"]
        plot = node["plot"]
        node_id = node["node_id"]
        
        # Concatenate title and plot (separated by a delimiter)
        combined_text = f"Title: {title}, Plot: {plot}"
        # Generate embedding for the combined text
        embedding = model.encode(combined_text)
        session.write_transaction(update_node_with_embedding, node_id, embedding)
        
print("Job done")

# Close the driver connection
driver.close()
