from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
def load_env_vars():
    # Load from .env file in the project root
    load_dotenv()
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables or .env file")
    return api_key

def create_vector_store(chunks, persist_directory="db"):
    api_key = load_env_vars()
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    
    # Create vector store with persist_directory
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=persist_directory
    )
    
    # The persist() method isn't needed with newer versions of Chroma
    # The data is automatically persisted when using persist_directory
    # Remove this line: vector_store.persist()
    
    return vector_store

def load_vector_store(persist_directory="db"):
    api_key = load_env_vars()
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def retrieve_chunks(query, vector_store, k=3):
    return vector_store.similarity_search(query, k=k)