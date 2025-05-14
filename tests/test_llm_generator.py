"""
Tests for the LLM generator module.
"""

from unittest.mock import MagicMock, patch

import pytest
from langchain.schema import Document

from src import config
from src.llm_generator import LLMGenerator


class TestLLMGenerator:
    """Test the LLMGenerator class."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default values."""
        with patch('src.llm_generator.Ollama') as mock_ollama:
            mock_llm = MagicMock()
            mock_ollama.return_value = mock_llm
            
            generator = LLMGenerator()
            
            assert generator.model_name == config.OLLAMA_MODEL
            assert generator.base_url == config.OLLAMA_BASE_URL
            assert generator.system_prompt == config.SYSTEM_PROMPT
            assert generator.rag_prompt_template == config.RAG_PROMPT_TEMPLATE
            assert generator.llm == mock_llm
            
            # Verify Ollama was initialized correctly
            mock_ollama.assert_called_once_with(
                model=config.OLLAMA_MODEL,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0.0
            )

    def test_init_with_custom_values(self) -> None:
        """Test initialization with custom values."""
        with patch('src.llm_generator.Ollama') as mock_ollama:
            mock_llm = MagicMock()
            mock_ollama.return_value = mock_llm
            
            custom_model = "custom-model"
            custom_url = "http://custom-url:11434"
            custom_system_prompt = "Custom system prompt"
            custom_template = "Custom {query} with {context}"
            
            generator = LLMGenerator(
                model_name=custom_model,
                base_url=custom_url,
                system_prompt=custom_system_prompt,
                rag_prompt_template=custom_template
            )
            
            assert generator.model_name == custom_model
            assert generator.base_url == custom_url
            assert generator.system_prompt == custom_system_prompt
            assert generator.rag_prompt_template == custom_template
            
            # Verify Ollama was initialized with custom values
            mock_ollama.assert_called_once_with(
                model=custom_model,
                base_url=custom_url,
                temperature=0.0
            )

    def test_process_retrieved_documents_empty(self) -> None:
        """Test processing empty retrieved documents."""
        with patch('src.llm_generator.Ollama'):
            generator = LLMGenerator()
            result = generator.process_retrieved_documents([])
            
            assert result["context"] == ""
            assert result["chunk_count"] == 0
            # When there are no documents, we now return zero scores instead of empty dict
            assert result["score_stats"] == {
                "min_score": 0.0,
                "max_score": 0.0,
                "avg_score": 0.0,
            }

    def test_process_retrieved_documents(self) -> None:
        """Test processing retrieved documents."""
        with patch('src.llm_generator.Ollama'):
            generator = LLMGenerator()
            
            # Create test documents
            docs = [
                Document(
                    page_content="Content 1",
                    metadata={"score": 0.8, "header_1": "Doc1", "header_2": "Section1"}
                ),
                Document(
                    page_content="Content 2",
                    metadata={"score": 0.6, "header_1": "Doc1", "header_2": "Section2"}
                ),
                Document(
                    page_content="Content 3",
                    metadata={"score": 0.7}
                )
            ]
            
            result = generator.process_retrieved_documents(docs)
            
            # Verify results
            assert "[Doc1 > Section1]\nContent 1" in result["context"]
            assert "[Doc1 > Section2]\nContent 2" in result["context"]
            assert "Content 3" in result["context"]
            assert result["chunk_count"] == 3
            assert "min_score" in result["score_stats"]
            assert "max_score" in result["score_stats"]
            assert "avg_score" in result["score_stats"]
            assert result["score_stats"]["min_score"] == 0.6
            assert result["score_stats"]["max_score"] == 0.8
            assert result["score_stats"]["avg_score"] == pytest.approx(0.7)

    def test_generate_answer(self) -> None:
        """Test generating an answer."""
        with patch('src.llm_generator.Ollama') as mock_ollama:
            # Setup mock LLM
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = "Generated answer"
            mock_ollama.return_value = mock_llm
            
            generator = LLMGenerator()
            
            # Mock process_retrieved_documents
            with patch.object(
                generator, 
                'process_retrieved_documents', 
                return_value={
                    "context": "Processed context",
                    "chunk_count": 2,
                    "score_stats": {"min_score": 0.6, "max_score": 0.8, "avg_score": 0.7}
                }
            ):
                # Create test documents
                docs = [
                    Document(page_content="Content 1", metadata={"score": 0.8}),
                    Document(page_content="Content 2", metadata={"score": 0.6})
                ]
                
                result = generator.generate_answer("Test query", docs)
                
                # Verify results
                assert result["query"] == "Test query"
                assert result["context"] == "Processed context"
                assert result["answer"] == "Generated answer"
                assert result["retrieval_info"]["chunk_count"] == 2
                assert result["retrieval_info"]["score_stats"]["min_score"] == 0.6
                assert result["retrieval_info"]["score_stats"]["max_score"] == 0.8
                assert result["retrieval_info"]["score_stats"]["avg_score"] == 0.7
                
                # Verify LLM was called with formatted prompt
                mock_llm.invoke.assert_called_once()
                call_args = mock_llm.invoke.call_args[0][0]
                assert "Test query" in call_args
                assert "Processed context" in call_args
