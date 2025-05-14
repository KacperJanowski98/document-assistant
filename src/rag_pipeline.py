"""
RAG pipeline module for coordinating document processing, retrieval, and generation.
"""
import os
import time
from typing import Any

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.schema import Document

from src.document_processor import DocumentProcessor
from src.embedding_manager import EmbeddingManager
from src.llm_generator import LLMGenerator
from src.ragas_evaluator import RAGASEvaluator


class RAGPipeline:
    """Class for coordinating the RAG pipeline."""

    def __init__(
        self,
        document_processor: DocumentProcessor | None = None,
        embedding_manager: EmbeddingManager | None = None,
        llm_generator: LLMGenerator | None = None,
        ragas_evaluator: RAGASEvaluator | None = None,
        enable_langsmith: bool = True,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            document_processor: DocumentProcessor instance.
            embedding_manager: EmbeddingManager instance.
            llm_generator: LLMGenerator instance.
            ragas_evaluator: RAGASEvaluator instance.
            enable_langsmith: Whether to enable LangSmith tracing.
        """
        self.document_processor = document_processor or DocumentProcessor()
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.llm_generator = llm_generator or LLMGenerator()
        self.enable_langsmith = enable_langsmith
        self.callback_manager = self._setup_callbacks() if enable_langsmith else None
        self.ragas_evaluator = ragas_evaluator or RAGASEvaluator(
            callback_manager=self.callback_manager
        )

    def _setup_callbacks(self) -> CallbackManager | None:
        """
        Set up callbacks for LangSmith tracing if applicable.

        Returns:
            Configured CallbackManager if LangSmith is enabled, None otherwise.
        """
        langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        
        if not langchain_api_key:
            print("Warning: LANGCHAIN_API_KEY not set. LangSmith tracing disabled.")
            return None
        
        try:
            tracer = LangChainTracer(
                project_name=os.getenv("LANGCHAIN_PROJECT", "document-assistant")
                )
            return CallbackManager([tracer])
        except Exception as e:
            print(f"Warning: Failed to initialize LangSmith tracer: {e}")
            return None

    def ingest_document(self, document_path: str) -> int:
        """
        Ingest a document into the vector store.

        Args:
            document_path: Path to the document to ingest.

        Returns:
            Number of chunks ingested.

        Raises:
            FileNotFoundError: If the document is not found.
        """
        start_time = time.time()
        
        print(f"Ingesting document: {document_path}")
        
        # Load the document
        content = self.document_processor.load_markdown(document_path)
        
        # Split the document
        chunks = self.document_processor.split_markdown(content)
        
        # Add to vector store
        self.embedding_manager.add_documents(chunks)
        
        elapsed_time = time.time() - start_time
        print(f"Ingestion completed in {elapsed_time:.2f} seconds. Added {len(chunks)} chunks.")
        
        return len(chunks)

    def retrieve_with_scores(self, query: str, top_k: int | None = None) -> list[tuple[Document, float]]:
        """
        Retrieve relevant documents with their similarity scores.

        Args:
            query: Query string.
            top_k: Number of documents to retrieve.

        Returns:
            List of (document, score) tuples.
        """
        # Get the vector store
        vector_store = self.embedding_manager.get_or_create_vector_store()
        
        # Perform similarity search with scores
        docs_and_scores = vector_store.similarity_search_with_score(
            query,
            k=top_k or self.embedding_manager.top_k_chunks or 5
        )
        
        # Add scores to document metadata
        for doc, score in docs_and_scores:
            doc.metadata["score"] = score
        
        return docs_and_scores

    def retrieve(self, query: str, top_k: int | None = None) -> list[Document]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Query string.
            top_k: Number of documents to retrieve.

        Returns:
            List of retrieved documents.
        """
        # Get documents with scores
        docs_and_scores = self.retrieve_with_scores(query, top_k)
        
        # Return just the documents (scores are now in metadata)
        return [doc for doc, _ in docs_and_scores]

    def query(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        """
        Process a query through the RAG pipeline.

        Args:
            query: Query string.
            top_k: Number of documents to retrieve.

        Returns:
            Dictionary containing query, retrieved context, generated answer, and metadata.
        """
        start_time = time.time()
        print(f"Processing query: {query}")
        
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, top_k)
        
        # Generate answer
        result = self.llm_generator.generate_answer(query, retrieved_docs)
        
        # Evaluate using RAGAS if enabled
        if self.ragas_evaluator.enable_evaluation:
            # Extract contexts as strings
            contexts = []
            for doc in retrieved_docs:
                contexts.append(doc.page_content)
            
            # Run RAGAS evaluation
            evaluation_scores = self.ragas_evaluator.evaluate(
                query=query,
                answer=result["answer"],
                contexts=contexts
            )
            
            # Add scores to result
            if evaluation_scores:
                result["ragas_metrics"] = evaluation_scores
        
        # Add timing information
        elapsed_time = time.time() - start_time
        result["metadata"] = {
            "processing_time": f"{elapsed_time:.2f} seconds"
        }
        
        return result
