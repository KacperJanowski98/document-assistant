#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Embedding manager module for handling embeddings and vector store.
"""
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings

from src import config


class EmbeddingManager:
    """Class for managing embeddings and vector store."""

    def __init__(
        self,
        embedding_model_provider: Optional[str] = None,
        embedding_model_name: Optional[str] = None,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """
        Initialize the embedding manager.

        Args:
            embedding_model_provider: Provider for embeddings ('huggingface' or 'ollama').
            embedding_model_name: Name of the embedding model.
            persist_directory: Directory to persist ChromaDB.
            collection_name: Name of the ChromaDB collection.
        """
        self.embedding_model_provider = embedding_model_provider or config.EMBEDDING_MODEL_PROVIDER
        self.embedding_model_name = embedding_model_name or config.EMBEDDING_MODEL_NAME
        self.persist_directory = persist_directory or config.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or config.CHROMA_COLLECTION_NAME

        # Create the persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize the embedding model
        self.embedding_model = self._initialize_embedding_model()
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Vector store will be initialized when needed
        self._vector_store = None

    def _initialize_embedding_model(self) -> Embeddings:
        """
        Initialize the embedding model based on the provider.

        Returns:
            Initialized embedding model.

        Raises:
            ValueError: If an unsupported embedding provider is specified.
        """
        if self.embedding_model_provider.lower() == "huggingface":
            return HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        elif self.embedding_model_provider.lower() == "ollama":
            return OllamaEmbeddings(model=self.embedding_model_name, base_url=config.OLLAMA_BASE_URL)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_model_provider}")

    def get_or_create_vector_store(self) -> Chroma:
        """
        Get or create the ChromaDB vector store.

        Returns:
            ChromaDB vector store.
        """
        if self._vector_store is None:
            # Check if the collection exists
            try:
                self.chroma_client.get_collection(self.collection_name)
                collection_exists = True
            except NotFoundError:  # Changed from ValueError to NotFoundError
                collection_exists = False

            # Initialize the vector store
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=self.persist_directory,
            )

            # Log whether we're using an existing collection or creating a new one
            if collection_exists:
                print(f"Using existing ChromaDB collection: {self.collection_name}")
            else:
                print(f"Created new ChromaDB collection: {self.collection_name}")

        return self._vector_store

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of document chunks with content and metadata.
        """
        vector_store = self.get_or_create_vector_store()
        
        # Extract content and metadata
        texts = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Add to the vector store
        vector_store.add_texts(texts=texts, metadatas=metadatas)
        
        # Persist the vector store
        vector_store.persist()
        print(f"Added {len(chunks)} chunks to ChromaDB collection: {self.collection_name}")

    def get_retriever(self, top_k: Optional[int] = None) -> Any:
        """
        Get a retriever for the vector store.

        Args:
            top_k: Number of chunks to retrieve.

        Returns:
            Retriever for the vector store.
        """
        vector_store = self.get_or_create_vector_store()
        search_kwargs = {"k": top_k or config.TOP_K_CHUNKS}
        return vector_store.as_retriever(search_kwargs=search_kwargs)
