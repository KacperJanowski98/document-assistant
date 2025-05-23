"""
Tests for the RAG pipeline module.
"""
import os
from unittest.mock import MagicMock, patch

import pytest
from langchain.schema import Document

from src.document_processor import DocumentProcessor
from src.embedding_manager import EmbeddingManager
from src.llm_generator import LLMGenerator
from src.ragas_evaluator import RAGASEvaluator
from src.rag_pipeline import RAGPipeline


class TestRAGPipeline:
    """Test the RAGPipeline class."""

    @pytest.fixture
    def mock_components(self) -> dict[str, MagicMock]:
        """Create mock components for testing."""
        mock_doc_processor = MagicMock(spec=DocumentProcessor)
        mock_embedding_manager = MagicMock(spec=EmbeddingManager)
        mock_llm_generator = MagicMock(spec=LLMGenerator)
        mock_ragas_evaluator = MagicMock(spec=RAGASEvaluator)
        
        return {
            "doc_processor": mock_doc_processor,
            "embedding_manager": mock_embedding_manager,
            "llm_generator": mock_llm_generator,
            "ragas_evaluator": mock_ragas_evaluator
        }

    def test_init_with_components(self, mock_components: dict[str, MagicMock]) -> None:
        """Test initialization with provided components."""
        pipeline = RAGPipeline(
            document_processor=mock_components["doc_processor"],
            embedding_manager=mock_components["embedding_manager"],
            llm_generator=mock_components["llm_generator"],
            ragas_evaluator=mock_components["ragas_evaluator"],
            enable_langsmith=False
        )
        
        assert pipeline.document_processor == mock_components["doc_processor"]
        assert pipeline.embedding_manager == mock_components["embedding_manager"]
        assert pipeline.llm_generator == mock_components["llm_generator"]
        assert pipeline.ragas_evaluator == mock_components["ragas_evaluator"]
        assert pipeline.enable_langsmith is False
        assert pipeline.callback_manager is None

    @patch('src.rag_pipeline.DocumentProcessor')
    @patch('src.rag_pipeline.EmbeddingManager')
    @patch('src.rag_pipeline.LLMGenerator')
    @patch('src.rag_pipeline.RAGASEvaluator')
    def test_init_with_defaults(self, mock_ragas_eval, mock_llm_gen, mock_emb_mgr, mock_doc_proc) -> None:  # noqa: ANN001
        """Test initialization with default values."""
        # Setup mocks
        mock_doc_proc_instance = MagicMock()
        mock_emb_mgr_instance = MagicMock()
        mock_llm_gen_instance = MagicMock()
        mock_ragas_eval_instance = MagicMock()
        
        mock_doc_proc.return_value = mock_doc_proc_instance
        mock_emb_mgr.return_value = mock_emb_mgr_instance
        mock_llm_gen.return_value = mock_llm_gen_instance
        mock_ragas_eval.return_value = mock_ragas_eval_instance
        
        # Initialize with defaults and LangSmith disabled for testing
        pipeline = RAGPipeline(enable_langsmith=False)
        
        # Verify defaults were used
        assert pipeline.document_processor == mock_doc_proc_instance
        assert pipeline.embedding_manager == mock_emb_mgr_instance
        assert pipeline.llm_generator == mock_llm_gen_instance
        assert pipeline.ragas_evaluator == mock_ragas_eval_instance
        
        # Verify classes were called with default values
        mock_doc_proc.assert_called_once_with()
        mock_emb_mgr.assert_called_once_with()
        mock_llm_gen.assert_called_once_with()
        mock_ragas_eval.assert_called_once_with(callback_manager=None)

    @patch.dict(os.environ, {"LANGCHAIN_API_KEY": "dummy_key", "LANGCHAIN_PROJECT": "test-project"})
    @patch('src.rag_pipeline.LangChainTracer')
    def test_setup_callbacks_with_api_key(self, mock_tracer) -> None:  # noqa: ANN001
        """Test setting up callbacks with API key present."""
        # Setup mocks
        mock_tracer_instance = MagicMock()
        mock_tracer.return_value = mock_tracer_instance
        
        # Initialize pipeline with LangSmith enabled
        pipeline = RAGPipeline(
            document_processor=MagicMock(),
            embedding_manager=MagicMock(),
            llm_generator=MagicMock(),
            enable_langsmith=True
        )
        
        # Verify LangChainTracer was called with correct project name
        mock_tracer.assert_called_once_with(project_name="test-project")
        
        # Verify callback_manager was set
        assert pipeline.callback_manager is not None

    @patch.dict(os.environ, {}, clear=True)  # Clear environment variables
    def test_setup_callbacks_without_api_key(self) -> None:
        """Test setting up callbacks without API key."""
        # Initialize pipeline with LangSmith enabled but no API key
        pipeline = RAGPipeline(
            document_processor=MagicMock(),
            embedding_manager=MagicMock(),
            llm_generator=MagicMock(),
            enable_langsmith=True
        )
        
        # Verify callback_manager is None when no API key is present
        assert pipeline.callback_manager is None

    def test_ingest_document(self, mock_components: dict[str, MagicMock]) -> None:
        """Test ingesting a document."""
        # Setup mocks
        mock_doc_processor = mock_components["doc_processor"]
        mock_embedding_manager = mock_components["embedding_manager"]
        
        mock_doc_processor.load_markdown.return_value = "Test document content"
        mock_doc_processor.split_markdown.return_value = [
            {"content": "Chunk 1", "metadata": {}},
            {"content": "Chunk 2", "metadata": {}}
        ]
        
        pipeline = RAGPipeline(
            document_processor=mock_doc_processor,
            embedding_manager=mock_embedding_manager,
            llm_generator=mock_components["llm_generator"],
            ragas_evaluator=mock_components["ragas_evaluator"],
            enable_langsmith=False
        )
        
        # Test document ingestion
        result = pipeline.ingest_document("test_doc.md")
        
        # Verify expected method calls
        mock_doc_processor.load_markdown.assert_called_once_with("test_doc.md")
        mock_doc_processor.split_markdown.assert_called_once_with("Test document content")
        mock_embedding_manager.add_documents.assert_called_once_with([
            {"content": "Chunk 1", "metadata": {}},
            {"content": "Chunk 2", "metadata": {}}
        ])
        
        # Verify result
        assert result == 2  # Number of chunks

    def test_retrieve(self, mock_components: dict[str, MagicMock]) -> None:
        """Test retrieving documents."""
        # Setup mocks
        mock_embedding_manager = mock_components["embedding_manager"]
        mock_vector_store = MagicMock()
        
        # Create test documents with scores
        doc1 = Document(page_content="Test content 1", metadata={})
        doc2 = Document(page_content="Test content 2", metadata={})
        docs_and_scores = [(doc1, 0.9), (doc2, 0.85)]
        
        mock_embedding_manager.get_or_create_vector_store.return_value = mock_vector_store
        mock_vector_store.similarity_search_with_score.return_value = docs_and_scores
        
        pipeline = RAGPipeline(
            document_processor=mock_components["doc_processor"],
            embedding_manager=mock_embedding_manager,
            llm_generator=mock_components["llm_generator"],
            ragas_evaluator=mock_components["ragas_evaluator"],
            enable_langsmith=False
        )
        
        # Test retrieval
        result = pipeline.retrieve("test query", top_k=5)
        
        # Verify expected method calls
        mock_embedding_manager.get_or_create_vector_store.assert_called_once()
        mock_vector_store.similarity_search_with_score.assert_called_once_with("test query", k=5)
        
        # Verify result
        assert len(result) == 2
        assert result[0].page_content == "Test content 1"
        assert result[0].metadata["score"] == 0.9
        assert result[1].page_content == "Test content 2"
        assert result[1].metadata["score"] == 0.85

    def test_query_with_ragas_enabled(self, mock_components: dict[str, MagicMock]) -> None:
        """Test querying the pipeline with RAGAS evaluation enabled."""
        # Setup mocks
        mock_embedding_manager = mock_components["embedding_manager"]
        mock_llm_generator = mock_components["llm_generator"]
        mock_ragas_evaluator = mock_components["ragas_evaluator"]
        mock_vector_store = MagicMock()
        
        # Create test documents with scores
        doc1 = Document(page_content="Test content", metadata={})
        docs_and_scores = [(doc1, 0.9)]
        
        mock_answer = {
            "query": "test query",
            "context": "Test content",
            "answer": "Generated answer",
            "retrieval_info": {
                "chunk_count": 1,
                "score_stats": {}
            }
        }
        mock_ragas_scores = {
            "faithfulness": 0.9,
            "answer_relevancy": 0.85,
            "context_precision": 0.92,
            "evaluation_time": 2.5
        }
        
        mock_embedding_manager.get_or_create_vector_store.return_value = mock_vector_store
        mock_vector_store.similarity_search_with_score.return_value = docs_and_scores
        mock_llm_generator.generate_answer.return_value = mock_answer
        mock_ragas_evaluator.enable_evaluation = True
        mock_ragas_evaluator.evaluate.return_value = mock_ragas_scores
        
        pipeline = RAGPipeline(
            document_processor=mock_components["doc_processor"],
            embedding_manager=mock_embedding_manager,
            llm_generator=mock_llm_generator,
            ragas_evaluator=mock_ragas_evaluator,
            enable_langsmith=False
        )
        
        # Test querying
        result = pipeline.query("test query", top_k=5)
        
        # Verify expected method calls
        mock_embedding_manager.get_or_create_vector_store.assert_called()
        mock_vector_store.similarity_search_with_score.assert_called_once_with("test query", k=5)
        mock_llm_generator.generate_answer.assert_called_once()
        mock_ragas_evaluator.evaluate.assert_called_once_with(
            query="test query",
            answer="Generated answer",
            contexts=["Test content"]
        )
        
        # Verify result
        assert result["query"] == "test query"
        assert result["context"] == "Test content"
        assert result["answer"] == "Generated answer"
        assert result["retrieval_info"]["chunk_count"] == 1
        assert "processing_time" in result["metadata"]
        assert result["ragas_metrics"] == mock_ragas_scores

    def test_query_with_ragas_disabled(self, mock_components: dict[str, MagicMock]) -> None:
        """Test querying the pipeline with RAGAS evaluation disabled."""
        # Setup mocks
        mock_embedding_manager = mock_components["embedding_manager"]
        mock_llm_generator = mock_components["llm_generator"]
        mock_ragas_evaluator = mock_components["ragas_evaluator"]
        mock_vector_store = MagicMock()
        
        # Create test documents with scores
        doc1 = Document(page_content="Test content", metadata={})
        docs_and_scores = [(doc1, 0.9)]
        
        mock_answer = {
            "query": "test query",
            "context": "Test content",
            "answer": "Generated answer",
            "retrieval_info": {
                "chunk_count": 1,
                "score_stats": {}
            }
        }
        
        mock_embedding_manager.get_or_create_vector_store.return_value = mock_vector_store
        mock_vector_store.similarity_search_with_score.return_value = docs_and_scores
        mock_llm_generator.generate_answer.return_value = mock_answer
        mock_ragas_evaluator.enable_evaluation = False
        
        pipeline = RAGPipeline(
            document_processor=mock_components["doc_processor"],
            embedding_manager=mock_embedding_manager,
            llm_generator=mock_llm_generator,
            ragas_evaluator=mock_ragas_evaluator,
            enable_langsmith=False
        )
        
        # Test querying
        result = pipeline.query("test query", top_k=5)
        
        # Verify RAGAS evaluation was not called
        mock_ragas_evaluator.evaluate.assert_not_called()
        
        # Verify result
        assert result["query"] == "test query"
        assert result["context"] == "Test content"
        assert result["answer"] == "Generated answer"
        assert result["retrieval_info"]["chunk_count"] == 1
        assert "processing_time" in result["metadata"]
        assert "ragas_metrics" not in result
