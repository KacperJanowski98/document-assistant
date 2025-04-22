#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM generator module for generating answers from retrieved contexts.
"""
from typing import Dict, List, Any, Optional

from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.schema import Document

from src import config


class LLMGenerator:
    """Class for generating answers using an LLM."""

    def __init__(
        self, 
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        rag_prompt_template: Optional[str] = None,
    ):
        """
        Initialize the LLM generator.

        Args:
            model_name: Name of the LLM model to use.
            base_url: Base URL for the Ollama API.
            system_prompt: System prompt for the LLM.
            rag_prompt_template: Template for constructing RAG prompts.
        """
        self.model_name = model_name or config.OLLAMA_MODEL
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.system_prompt = system_prompt or config.SYSTEM_PROMPT
        self.rag_prompt_template = rag_prompt_template or config.RAG_PROMPT_TEMPLATE
        
        # Initialize the LLM
        self.llm = self._initialize_llm()
        
        # Initialize the prompt template
        self.prompt = PromptTemplate(
            template=self.rag_prompt_template,
            input_variables=["system_prompt", "context", "query"]
        )

    def _initialize_llm(self):
        """
        Initialize the Ollama LLM.

        Returns:
            Initialized Ollama LLM.
        """
        return Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0.0,  # Use a low temperature for more deterministic answers
        )

    def process_retrieved_documents(self, docs: List[Document]) -> Dict[str, Any]:
        """
        Process retrieved documents to get context and similarity scores.

        Args:
            docs: List of retrieved documents.

        Returns:
            Dictionary containing structured information about retrieved documents.
        """
        contexts = []
        scores = []
        
        for doc in docs:
            # Get content and score
            context = doc.page_content
            score = doc.metadata.get("score", 0) if hasattr(doc, "metadata") else 0
            
            # Get headers if available
            headers = []
            for level in range(1, 5):
                header_key = f"header_{level}"
                if header_key in doc.metadata:
                    headers.append(doc.metadata[header_key])
            
            # Format context with headers if available
            if headers:
                header_text = " > ".join(headers)
                formatted_context = f"[{header_text}]\n{context}"
            else:
                formatted_context = context
            
            contexts.append(formatted_context)
            scores.append(score)
        
        # Combine contexts with separator
        combined_context = "\n\n---\n\n".join(contexts)
        
        # Calculate similarity score statistics if scores are available
        score_stats = {}
        if scores:
            score_stats = {
                "min_score": min(scores),
                "max_score": max(scores),
                "avg_score": sum(scores) / len(scores),
            }
        
        return {
            "context": combined_context,
            "chunk_count": len(docs),
            "score_stats": score_stats
        }

    def generate_answer(self, query: str, retrieved_docs: List[Document]) -> Dict[str, Any]:
        """
        Generate an answer based on the query and retrieved documents.

        Args:
            query: User query.
            retrieved_docs: List of retrieved documents.

        Returns:
            Dictionary containing the generated answer and retrieval info.
        """
        # Process retrieved documents
        processed_data = self.process_retrieved_documents(retrieved_docs)
        
        # Format the prompt
        formatted_prompt = self.prompt.format(
            system_prompt=self.system_prompt,
            context=processed_data["context"],
            query=query
        )
        
        # Generate the answer
        answer = self.llm.invoke(formatted_prompt)
        
        # Return answer and retrieval info
        return {
            "query": query,
            "context": processed_data["context"],
            "answer": answer,
            "retrieval_info": {
                "chunk_count": processed_data["chunk_count"],
                "score_stats": processed_data["score_stats"]
            }
        }
