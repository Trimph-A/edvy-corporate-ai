import os
import io
import json
import logging
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import IBMWatsonLLM
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from yaml import safe_load
from .utils import load_config

config = load_config("config/config.yaml")
WATSONX_API_URL = f"https://{config['watsonx']['region']}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
WATSONX_API_KEY = config['watsonx']['api_key']
WATSONX_PROJECT_ID = config['watsonx']['project_id']
WATSONX_MODEL_ID = config['watsonx']['model_id']

router = APIRouter()
logger = logging.getLogger(__name__)

class TrainingResponse(BaseModel):
    status: str
    message: str

@router.post(
    "/upload-documents",
    response_model=TrainingResponse,
    summary="Upload documents and train a conversational model",
    description="""
    Upload one or more documents (PDFs) that describe the company's policies, goals, history, or other key details. 
    The system will extract content from these documents and train a conversational model to answer related questions.
    """
)
async def upload_documents(
    files: List[UploadFile] = File(..., description="Upload PDF files for training the model.")
) -> TrainingResponse:
    logger.info(f"Received {len(files)} files for training.")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    # Step 1: Extract text from PDFs
    documents = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Skipping non-PDF file: {file.filename}")
            continue
        try:
            content = await file.read()
            loader = PyPDFLoader(io.BytesIO(content))
            docs = loader.load_and_split()
            documents.extend(docs)
            logger.info(f"Successfully extracted text from {file.filename}")
        except Exception as e:
            logger.error(f"Failed to extract text from {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {e}")
    
    if not documents:
        raise HTTPException(status_code=400, detail="No valid content extracted from uploaded files.")

    # Step 2: Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split documents into {len(chunks)} chunks.")

    # Step 3: Build vector store using FAISS
    try:
        vector_store = FAISS.from_documents(chunks, embedding_model="sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Vector store created successfully.")
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        raise HTTPException(status_code=500, detail="Failed to create vector store.")

    # Step 4: Train the Conversational Model
    try:
        retriever = vector_store.as_retriever()
        retriever.search_kwargs["k"] = 5  
        global trained_chain
        trained_chain = ConversationalRetrievalChain(
            retriever=retriever,
            llm=IBMWatsonLLM(api_key=WATSONX_API_KEY)
        )
        logger.info("Conversational model trained successfully.")
    except Exception as e:
        logger.error(f"Failed to train conversational model: {e}")
        raise HTTPException(status_code=500, detail="Failed to train conversational model.")

    return TrainingResponse(status="Success", message="Conversational model trained successfully.")
