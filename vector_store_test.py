#-------------------------------------------------------------------------------
# Name:        vectore_store_test
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

DOCUMENT_URL ="https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
LOCAL_FILENAME = "policy.pdf"
CHROMA_COLLECTION_NAME = "hackrx_policy"
print("Loading sentence Transformer model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model Loaded.")


#Main block
if __name__=="__main__":
    client = chromadb.Client()
    try:
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        print(f"Collection '{CHROMA_COLLECTION_NAME}' already exists. Skipping ingestion.")
    except Exception:
        print(f"Collection '{CHROMA_COLLECTION_NAME}' not found.Ingesting data...")
        collection = client.create_collection(name=CHROMA_COLLECTION_NAME)

        if download_file(DOCUMENT_URL,LOCAL_FILENAME):
            extracted_text = extract_text_from_pdf(LOCAL_FILENAME)

            if extracted_text:
                chunks = chunk_text(extracted_text)
                create_and_store_embeddings(chunks, collection)

            os.remove(LOCAL_FILENAME)
            print(f"Cleaned up local file: {LOCAL_FILENAME}")

    print("\n---Testing Semantic Search---")
    question = "What is the waiting period for pre-existing diseases?"

    query_embedding = embedding_model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    print(f"Searching for: '{question}'")
    print("\nFound the following relevant chunks:")
    for doc in results['documents'][0]:
        print("---")
        print(doc)