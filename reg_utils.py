#-------------------------------------------------------------------------------
# Name:        rag_utils
# Purpose:
#
# Author:      Dell
#
# Created:     06-08-2025
# Copyright:   (c) Dell 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import requests
import fitz
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from typing import List
from pinecone import Pinecone

def download_file(url: str, filename: str) -> bool:
    """Downloads a file from a URL and saves it locally. Returns True on success, False on failure."""
    print(f"Downloading file from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # This will raise an exception for bad status codes (4xx or 5xx)

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded and saved as {filename}")
        return True  # Download was successful
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        return False # Download failed

def extract_text_from_pdf(filename):
    """Extracts text from a local PDF file."""
    print(f"Extracting text from {filename}...")
    text_content = ""
    try:
        with fitz.open(filename) as doc:
            for page in doc:
                text_content += page.get_text()
        print("Text extraction successful!")
        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

#functions for chunking and embedding
def chunk_text(text: str) -> List[str]:
    print("Chunnking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n","\n"," ",""]
    )
    chunks = text_splitter.split_text(text)
    print(f"Original document split into {len(chunks)} chunks.")
    return chunks


def create_and_store_embeddings(chunks: List[str], embedding_model: SentenceTransformer, index):
    """
    Creates embeddings for each chunk and stores them in a Pinecone index.
    """
    print("Creating embeddings and storing in Pinecone...")
    
    # Pinecone upsert method expects data in a specific format
    # (id, embedding vector, metadata)
    data_to_upsert = []
    
    # Create the embeddings
    embeddings = embedding_model.encode(chunks)
    
    for i, chunk in enumerate(chunks):
        # Create a unique ID for each chunk
        doc_id = f"doc_{i}"
        
        # Prepare the tuple for upserting
        data_to_upsert.append((doc_id, embeddings[i].tolist(), {"text": chunk}))
        
    # Upsert the data in batches for better performance
    index.upsert(vectors=data_to_upsert)
    
    print("Embeddings stored in Pinecone.")
