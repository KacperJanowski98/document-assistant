#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration module for the document assistant application.
"""
import os
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Ollama settings
OLLAMA_MODEL = "mistral"  # Default LLM model from Ollama
OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama API URL

# Embedding settings
EMBEDDING_MODEL_PROVIDER = "huggingface"  # Options: "huggingface", "ollama"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"  # Default for HuggingFace

# ChromaDB settings
CHROMA_PERSIST_DIRECTORY = str(OUTPUT_DIR / "chroma_db")
CHROMA_COLLECTION_NAME = "document_chunks"

# Document processing settings
CHUNK_SIZE = 1000  # Default chunk size for text splitting
CHUNK_OVERLAP = 200  # Default chunk overlap for text splitting

# Retrieval settings
TOP_K_CHUNKS = 5  # Number of chunks to retrieve for RAG

# RAGAs evaluation settings
ENABLE_RAGAS_EVAL = True  # Toggle for RAGAS evaluation

# Prompt templates
SYSTEM_PROMPT = """
You are a technical document assistant. Your task is to provide accurate and helpful information from 
technical documents, especially communication protocol specifications.

Always stay faithful to the provided context. If the information to answer the query is not present 
in the context, clearly state that you don't have that information.
"""

RAG_PROMPT_TEMPLATE = """
System: {system_prompt}

Context information is below.
-----------------------------
{context}
-----------------------------

Given the context information and not prior knowledge, answer the following query.
Query: {query}

Answer:
"""


def get_config_summary():
    """Return a summary of the current configuration."""
    return {
        "ollama_model": OLLAMA_MODEL,
        "embedding_model_provider": EMBEDDING_MODEL_PROVIDER,
        "embedding_model_name": EMBEDDING_MODEL_NAME,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "top_k_chunks": TOP_K_CHUNKS,
        "enable_ragas_eval": ENABLE_RAGAS_EVAL,
    }
