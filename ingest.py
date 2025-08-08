#-------------------------------------------------------------------------------
# Name:        ingest.py
# Purpose: contains document processing code
#
# Author:      Dell
#
# Created:     07-08-2025
# Copyright:   (c) Dell 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from reg_utils import download_file, extract_text_from_pdf, chunk_text, create_and_store_embeddings
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

# Use Pinecone instead of ChromaDB
from pinecone import Pinecone

# --- Globals and Configuration ---
# Your document URL here. This is the document your script will download.
DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
LOCAL_FILENAME = "policy.pdf"

# Load environment variables (make sure they are in your .env)
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
DIMENSION = 384 # The dimension of your embedding model

# Check if required environment variables are set
if not PINECONE_API_KEY or not INDEX_NAME:
    raise ValueError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set in your .env file.")

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)


# --- Main execution block ---
if __name__ == "__main__":
    index_names = [index.name for index in pc.list_indexes()]
    # Check if the index exists. If not, create it.
    if INDEX_NAME not in index_names:
        print(f"Index '{INDEX_NAME}' not found. Creating it now...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric='cosine',
            spec={"serverless": {"cloud": "aws", "region": "us-east-1"}} # Correct way to specify spec
        )
        print(f"Index '{INDEX_NAME}' created successfully.")
    
    # Connect to the index
    index = pc.Index(INDEX_NAME)

    # --- Document Ingestion Pipeline ---
    print("\n--- Starting document ingestion pipeline ---")
    local_file_path = f'./{LOCAL_FILENAME}'
    
    try:
        if download_file(DOCUMENT_URL, local_file_path):
            extracted_text = extract_text_from_pdf(local_file_path)
            if extracted_text:
                chunks = chunk_text(extracted_text)
                create_and_store_embeddings(chunks, embedding_model, index)
                print("Document ingestion complete.")
            else:
                print("Text extraction failed. Ingestion aborted.")
    finally:
        # This ensures the local file is always deleted
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"\nCleaned up local file: {local_file_path}")