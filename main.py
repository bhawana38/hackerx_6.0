#-------------------------------------------------------------------------------
# Name:        main.py
# Purpose:
#
# Author:      Dell
#
# Created:     04-08-2025
# Copyright:   (c) Dell 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException, Depends, Security
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
from typing import List
# The chroma library is not needed for this version
from openai import OpenAI
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# --- Environment variables for API keys ---
load_dotenv()
API_KEY=os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
# Pinecone environment variable is no longer needed

# --- Client and Index Initializations ---
# This is the correct way to initialize the clients for a cloud-first approach
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
index = pinecone_client.Index(INDEX_NAME)

openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
)

# --- Pydantic Model for the Request Body ---
# This was the missing definition
class HackRXRequest(BaseModel):
    documents: str
    questions: List[str]

# --- Security Dependency ---
# This function must be defined BEFORE it is used by an endpoint
async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    This function is a dependency that checks if the provided API key is valid.
    """
    if not api_key_header or not api_key_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token is missing or invalid.")
    
    bearer_token = api_key_header.split(" ")[1]
    
    if bearer_token == API_KEY:
        return bearer_token
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

# --- FastAPI App and Endpoints ---
# The app instance MUST be defined before it is used
app = FastAPI()

@app.post("/hackrx/run")
async def run_hackrx(request_data: HackRXRequest, api_key: str = Depends(get_api_key)):
    answers = []
    
    for question in request_data.questions:
        # Step 1: Create embedding for the query using OpenAI
        # This must match the embedding model used in the ingestion script
        query_embedding_response = openai_client.embeddings.create(
            input=[question],
            model="text-embedding-3-small"
        )
        query_embedding = query_embedding_response.data[0].embedding
        
        # Step 2: Query Pinecone for the most relevant document chunks
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
        )
        
        # Step 3: Augment the prompt with retrieved context
        retrieved_context = "\n\n---\n\n".join([r['metadata']['text'] for r in results.matches])
        
        # Step 4: Generate the answer using the LLM
        if not retrieved_context.strip():
            answer = "I cannot answer based on the provided document as no relevant context was found."
        else:
            llm_prompt = f"""
            You are an intelligent assistant. Use only the following context to answer the question.
            If the answer is not in the context, say "I cannot answer based on the provided document."
            
            Context:
            {retrieved_context}
            
            Question:
            {question}
            """
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o", # Or a different model like "gpt-3.5-turbo"
                    messages=[{"role": "user", "content": llm_prompt}],
                )
                answer = response.choices[0].message.content
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"LLM API error: {e}")
        
        answers.append(answer)
        
    return {"answers": answers}