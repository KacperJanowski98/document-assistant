#!/usr/bin/env python
"""
Tests for the embedding manager module.
"""
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from chromadb.errors import NotFoundError

from src import config
from src.embedding_manager import EmbeddingManager


class TestEmbeddingManager:
    """Test the EmbeddingManager class."""
    
    @pytest.fixture
    def temp_chroma_dir(self):  # noqa: ANN201
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up after test
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @patch('src.embedding_manager.HuggingFaceEmbeddings')
    def test_init_with_huggingface(self, mock_hf_embeddings, temp_chroma_dir) -> None:  # noqa: ANN001
        """Test initialization with HuggingFace embeddings."""
        mock_hf_instance = MagicMock()
        mock_hf_embeddings.return_value = mock_hf_instance
        
        manager = EmbeddingManager(
            embedding_model_provider="huggingface",
            embedding_model_name="test-embeddings",
            persist_directory=temp_chroma_dir,
            collection_name="test_collection"
        )
        
        assert manager.embedding_model_provider == "huggingface"
        assert manager.embedding_model_name == "test-embeddings"
        assert manager.persist_directory == temp_chroma_dir
        assert manager.collection_name == "test_collection"
        
        # Verify HuggingFaceEmbeddings was called with correct params
        mock_hf_embeddings.assert_called_once_with(model_name="test-embeddings")
        assert manager.embedding_model == mock_hf_instance
    
    @patch('src.embedding_manager.OllamaEmbeddings')
    def test_init_with_ollama(self, mock_ollama_embeddings, temp_chroma_dir) -> None:  # noqa: ANN001
        """Test initialization with Ollama embeddings."""
        mock_ollama_instance = MagicMock()
        mock_ollama_embeddings.return_value = mock_ollama_instance
        
        manager = EmbeddingManager(
            embedding_model_provider="ollama",
            embedding_model_name="test-embeddings",
            persist_directory=temp_chroma_dir,
            collection_name="test_collection"
        )
        
        # Verify OllamaEmbeddings was called with correct params
        mock_ollama_embeddings.assert_called_once_with(
            model="test-embeddings", 
            base_url=config.OLLAMA_BASE_URL
        )
        assert manager.embedding_model == mock_ollama_instance
    
    def test_init_with_unsupported_provider(self, temp_chroma_dir) -> None:  # noqa: ANN001
        """Test initialization with an unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported embedding provider"):
            EmbeddingManager(
                embedding_model_provider="unsupported",
                persist_directory=temp_chroma_dir
            )
    
    @patch('src.embedding_manager.Chroma')
    @patch('src.embedding_manager.HuggingFaceEmbeddings')
    @patch('src.embedding_manager.chromadb.PersistentClient')
    def test_get_or_create_vector_store(
        self, mock_client, mock_hf_embeddings, mock_chroma, temp_chroma_dir  # noqa: ANN001
        ) -> None:  # noqa: ANN001
        """Test getting or creating a vector store."""
        # Mock setup
        mock_hf_instance = MagicMock()
        mock_hf_embeddings.return_value = mock_hf_instance
        
        mock_chroma_instance = MagicMock()
        mock_chroma.return_value = mock_chroma_instance
        
        # Setup mock client to throw NotFoundError
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get_collection.side_effect = NotFoundError("Collection does not exist")
        
        manager = EmbeddingManager(
            embedding_model_provider="huggingface",
            persist_directory=temp_chroma_dir
        )
        
        # Reset the mocks for clearer assertions
        mock_chroma.reset_mock()
        
        # Test getting the vector store
        result = manager.get_or_create_vector_store()
        
        # Verify Chroma was initialized correctly
        mock_chroma.assert_called_once_with(
            collection_name=manager.collection_name,
            embedding_function=mock_hf_instance,
            persist_directory=temp_chroma_dir
        )
        
        assert result == mock_chroma_instance
        
        # Test getting the same vector store again (should reuse)
        mock_chroma.reset_mock()
        result2 = manager.get_or_create_vector_store()
        
        # Verify Chroma wasn't called again
        mock_chroma.assert_not_called()
        assert result2 == mock_chroma_instance
    
    @patch('src.embedding_manager.EmbeddingManager.get_or_create_vector_store')
    def test_add_documents(self, mock_get_vector_store, temp_chroma_dir) -> None:  # noqa: ANN001
        """Test adding documents to the vector store."""
        # Mock setup
        mock_vector_store = MagicMock()
        mock_get_vector_store.return_value = mock_vector_store
        
        manager = EmbeddingManager(
            embedding_model_provider="huggingface",
            persist_directory=temp_chroma_dir
        )
        
        # Test data
        chunks = [
            {"content": "Test content 1", "metadata": {"header_1": "Test"}},
            {"content": "Test content 2", "metadata": {"header_1": "Test", "header_2": "Section"}}
        ]
        
        # Add documents
        manager.add_documents(chunks)
        
        # Verify vector store methods were called correctly
        mock_vector_store.add_texts.assert_called_once_with(
            texts=["Test content 1", "Test content 2"],
            metadatas=[{"header_1": "Test"}, {"header_1": "Test", "header_2": "Section"}]
        )
        mock_vector_store.persist.assert_called_once()
    
    @patch('src.embedding_manager.EmbeddingManager.get_or_create_vector_store')
    def test_get_retriever(self, mock_get_vector_store, temp_chroma_dir) -> None:  # noqa: ANN001
        """Test getting a retriever."""
        # Mock setup
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_get_vector_store.return_value = mock_vector_store
        
        manager = EmbeddingManager(
            embedding_model_provider="huggingface",
            persist_directory=temp_chroma_dir
        )
        
        # Get retriever with default k
        result = manager.get_retriever()
        
        # Verify as_retriever was called correctly
        mock_vector_store.as_retriever.assert_called_once_with(
            search_type="similarity",
            search_kwargs={"k": config.TOP_K_CHUNKS}
        )
        assert result == mock_retriever
        
        # Reset mock and test with custom k
        mock_vector_store.as_retriever.reset_mock()
        
        result = manager.get_retriever(top_k=10)
        
        # Verify as_retriever was called with custom k
        mock_vector_store.as_retriever.assert_called_once_with(
            search_type="similarity",
            search_kwargs={"k": 10}
        )
