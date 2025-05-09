from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_and_chunk_pdfs(pdf_dir="data", chunk_size=500, chunk_overlap=50):
    all_documents = []
    processed_files = 0
    failed_files = 0
    
    # Ensure directory exists
    if not os.path.exists(pdf_dir):
        logging.error(f"Directory {pdf_dir} does not exist")
        return []
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_dir, filename)
            try:
                # Try standard PyPDFLoader first
                logging.info(f"Processing {filename} with PyPDFLoader")
                loader = PyPDFLoader(path)
                documents = loader.load()
                
                # Check if we actually got content
                if len(documents) == 0 or all(not doc.page_content.strip() for doc in documents):
                    logging.warning(f"PyPDFLoader extracted no text from {filename}, trying UnstructuredPDFLoader")
                    # Fall back to UnstructuredPDFLoader for more complex PDFs
                    loader = UnstructuredPDFLoader(path)
                    documents = loader.load()
                
                all_documents.extend(documents)
                processed_files += 1
                logging.info(f"Successfully processed {filename}, extracted {len(documents)} pages")
                
            except Exception as e:
                logging.error(f"Error processing {filename}: {str(e)}")
                failed_files += 1
    
    # Use RecursiveCharacterTextSplitter for better chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    if all_documents:
        chunks = splitter.split_documents(all_documents)
        logging.info(f"Created {len(chunks)} chunks from {processed_files} files")
    else:
        logging.warning("No documents were successfully processed")
    
    if failed_files > 0:
        logging.warning(f"Failed to process {failed_files} files")
    
    return chunks