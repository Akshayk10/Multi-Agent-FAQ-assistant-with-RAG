from vector_store import create_vector_store, load_vector_store
from ingest_documents import load_and_chunk_pdfs

def initialize_database():
    # Load and chunk PDFs
    print("Loading and chunking PDFs...")
    chunks = load_and_chunk_pdfs()
    
    # Create vector store
    print(f"Creating vector store with {len(chunks)} chunks...")
    vector_store = create_vector_store(chunks)
    
    # Verify the vector store
    test_vs = load_vector_store()
    count = len(test_vs.get()['ids'])
    print(f"Vector store created with {count} chunks.")
    
    return vector_store

if __name__ == "__main__":
    # Run this script once to initialize your database
    initialize_database()