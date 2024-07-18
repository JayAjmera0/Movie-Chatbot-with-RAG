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
