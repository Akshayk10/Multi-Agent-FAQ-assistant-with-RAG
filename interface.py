__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import json
import streamlit as st
from agents import agent_router
from vector_store import create_vector_store, load_vector_store
from ingest_documents import load_and_chunk_pdfs

# Setup Google Cloud credentials from Streamlit secrets
if "gcp_service_account" in st.secrets:
    # Get credentials directly from Streamlit secrets
    credentials = st.secrets["gcp_service_account"]
    
    # Create a temporary credentials file
    credentials_json = json.dumps(credentials)
    with open("temp_credentials.json", "w") as f:
        f.write(credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_credentials.json"
    
    # Alternative: Use credentials directly in code if needed
    # from google.oauth2.service_account import Credentials
    # gcp_credentials = Credentials.from_service_account_info(credentials)
else:
    st.warning("GCP credentials not found in Streamlit secrets. Some features may not work.")

# Page configuration
st.set_page_config(page_title="Multi-Agent FAQ Assistant", layout="wide")

def ensure_vector_store_exists():
    """Check if vector store exists, initialize if not."""
    if not os.path.exists("db") or not os.path.isdir("db") or len(os.listdir("db")) == 0:
        st.info("Initializing vector store... This may take a moment.")
        # Check if data directory and PDFs exist
        if not os.path.exists("data"):
            os.makedirs("data")
            st.warning("No documents found. Please upload documents.")
            return False
        pdf_files = [f for f in os.listdir("data") if f.endswith('.pdf')]
        if not pdf_files:
            st.warning("No PDF files found in data directory. Please upload documents.")
            return False
        chunks = load_and_chunk_pdfs()
        create_vector_store(chunks)
        st.success("Vector store initialized!")
    return True

def pdf_uploader():
    """Handle PDF file uploads and processing."""
    st.sidebar.header("Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDF files",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.sidebar.button("Process Uploaded Files"):
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded files
            for file in uploaded_files:
                with open(f"data/{file.name}", "wb") as f:
                    f.write(file.getbuffer())
            
            # Process files and create vector store
            with st.spinner("Processing documents..."):
                chunks = load_and_chunk_pdfs()
                create_vector_store(chunks)
            
            st.sidebar.success(f"Processed {len(uploaded_files)} files!")
            # Refresh the app
            st.rerun()

# Main app logic
def main():
    st.title("📘 Multi-Agent FAQ Assistant")
    
    # File upload and vector store initialization
    pdf_uploader()
    vs_exists = ensure_vector_store_exists()
    
    # Load vector store if available
    vector_store = load_vector_store() if vs_exists else None
    
    # Check if vector store is empty
    if vector_store and len(vector_store.get()['ids']) == 0:
        st.error("Vector store is empty. Please upload and process documents first.")
        st.stop()
    
    # Query input and processing
    query = st.text_input("🔍 Ask a question")
    if query and vector_store:
        with st.spinner("Thinking..."):
            result = agent_router(query, vector_store)
        
        # Display results
        st.markdown(f"### 🔧 Tool Used: `{result['tool']}`")
        if "snippets" in result:
            st.markdown("### 📚 Retrieved Context:")
            for i, snippet in enumerate(result["snippets"]):
                st.write(f"**Snippet {i+1}:** {snippet[:400]}...")
        
        st.markdown("### 💬 Answer:")
        st.success(result["answer"])
    
    # Show status if no query has been made yet
    elif not query:
        st.info("Please enter a question to get started.")

# Run the app
if __name__ == "__main__":
    main()

# Cleanup temporary credentials file at app shutdown
def cleanup():
    if os.path.exists("temp_credentials.json"):
        try:
            os.remove("temp_credentials.json")
        except:
            pass

import atexit
atexit.register(cleanup)
