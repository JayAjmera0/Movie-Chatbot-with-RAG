# Movie Recommendation System with Neo4j and RAG

## Overview

This project is a sophisticated movie recommendation system leveraging a Neo4j graph database to create a vector index of movie plot embeddings and related information such as actors, directors, and more. The system is a Retrieval-Augmented Generation (RAG) application using LangChain agents and the Gemini API to answer movie-related queries.

## Features

- *Data Scraping*: Python script to scrape movie data from the internet.
- *Data Preprocessing*: Cleaning and preprocessing of scraped data.
- *Graph Database*: Storage of preprocessed data in a Neo4j graph database.
- *Vector Indexing*: Creation of vector embeddings for movie plots and related information.
- *Query Handling*: Answering movie-related questions using LangChain agents and the Gemini API.
- *Similarity Search*: Vector similarity search in Neo4j to find relevant movie information.

## Workflow

1. *Data Collection*:
    - Python script scrapes data from the internet.
2. *Data Preprocessing*:
    - Clean and preprocess the scraped data.
3. *Data Storage*:
    - Store the cleaned data in a Neo4j graph database.
4. *Embedding Creation*:
    - Create embeddings of movie plots and related information.
5. *Query Processing*:
    - Make embeddings of user queries.
    - Search Neo4j for nodes with similarity scores above 0.7.
    - Refine and return the output using LangChain agents and the Gemini API.

## Technologies Used

- *Neo4j*: Graph database for storing movie data and vector embeddings.
- *LangChain*: Agents for natural language processing and query handling.
- *Gemini API*: API for enhancing query responses.
- *Python*: For data scraping, preprocessing, and embedding creation.

## Installation

### Prerequisites

- Python 3.x
- Neo4j
- Required Python libraries (listed in requirements.txt)

### Setup

1. *Clone the repository*:
    sh
    git clone https://github.com/JayAjmera0/Movie-Chatbot-with-RAG.git
    
2. *Navigate to the project directory*:
    sh
    cd yourrepository
    
3. *Install dependencies*:
    sh
    pip install -r requirements.txt
    
4. *Set up Neo4j*:
    - Install Neo4j and start the database.
    - Configure connection settings in the project.

## Usage

1. *Run the data scraping script*:
    sh
    python scrape_data.py
    
2. *Run the data preprocessing script*:
    sh
    python preprocess_data.py
    
3. *Load data into Neo4j*:
    sh
    python load_data_neo4j.py
    
4. *Start the application*:
    sh
    python app.py
    

## Query Example

To ask for a good action movie recommendation, you might use:
```sh
curl -X POST -H "Content-Type: application/json" -d '{"question": "Suggest me a good action movie"}' http://localhost:8000/query
