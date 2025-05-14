"""
Tests for the RAGAS evaluator module.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.ragas_evaluator import RAGASEvaluator


class TestRAGASEvaluator:
    """Test class for RAGASEvaluator."""

    @pytest.fixture
    def evaluator(self):
        """Create a RAGASEvaluator instance for testing."""
        return RAGASEvaluator(enable_evaluation=True)

    @pytest.fixture
    def disabled_evaluator(self):
        """Create a disabled RAGASEvaluator instance for testing."""
        return RAGASEvaluator(enable_evaluation=False)

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        evaluator = RAGASEvaluator()
        assert evaluator.enable_evaluation == True  # Default from config
        assert evaluator.callback_manager is None
        assert len(evaluator.metrics) == 3

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        callback_manager = MagicMock()
        evaluator = RAGASEvaluator(
            enable_evaluation=False,
            callback_manager=callback_manager
        )
        assert evaluator.enable_evaluation is False
        assert evaluator.callback_manager == callback_manager

    def test_prepare_dataset(self, evaluator):
        """Test dataset preparation."""
        query = "What is RAG?"
        answer = "RAG stands for Retrieval-Augmented Generation."
        contexts = ["Context 1", "Context 2"]
        
        dataset = evaluator.prepare_dataset(query, answer, contexts)
        
        assert dataset["questions"] == [query]
        assert dataset["answers"] == [answer]
        assert dataset["contexts"] == [contexts]
        assert len(dataset["questions"]) == 1
        assert len(dataset["answers"]) == 1
        assert len(dataset["contexts"]) == 1

    def test_evaluate_disabled(self, disabled_evaluator):
        """Test evaluation when disabled."""
        result = disabled_evaluator.evaluate(
            query="Test",
            answer="Test answer",
            contexts=["Test context"]
        )
        assert result is None

    @patch("src.ragas_evaluator.evaluate")
    def test_evaluate_success(self, mock_evaluate, evaluator):
        """Test successful evaluation."""
        # Mock the RAGAS evaluate function
        mock_result = MagicMock()
        mock_result.scores = {
            "faithfulness": 0.9,
            "answer_relevancy": 0.85,
            "context_precision": 0.92,
        }
        mock_evaluate.return_value = mock_result
        
        # Run evaluation
        query = "What is RAG?"
        answer = "RAG stands for Retrieval-Augmented Generation."
        contexts = ["Context about RAG"]
        
        result = evaluator.evaluate(query, answer, contexts)
        
        # Verify the result
        assert result is not None
        assert result["faithfulness"] == 0.9
        assert result["answer_relevancy"] == 0.85
        assert result["context_precision"] == 0.92
        assert "evaluation_time" in result
        
        # Verify evaluate was called with correct arguments
        mock_evaluate.assert_called_once()
        call_args = mock_evaluate.call_args
        assert call_args.kwargs["dataset"]["questions"] == [query]
        assert call_args.kwargs["dataset"]["answers"] == [answer]
        assert call_args.kwargs["dataset"]["contexts"] == [[contexts[0]]]
        assert call_args.kwargs["metrics"] == evaluator.metrics

    @patch("src.ragas_evaluator.evaluate")
    @patch("src.ragas_evaluator.RunConfig")
    def test_evaluate_with_callback_manager(self, mock_runconfig, mock_evaluate, evaluator):
        """Test evaluation with callback manager."""
        callback_manager = MagicMock()
        evaluator.callback_manager = callback_manager
        
        mock_result = MagicMock()
        mock_result.scores = {"faithfulness": 0.9, "answer_relevancy": 0.85, "context_precision": 0.92}
        mock_evaluate.return_value = mock_result
        
        # Mock RunConfig
        mock_runconfig_instance = MagicMock()
        mock_runconfig.return_value = mock_runconfig_instance
        
        result = evaluator.evaluate("query", "answer", ["context"])
        
        # Verify RunConfig was created
        mock_runconfig.assert_called_once()
        
        # Verify evaluate was called with the RunConfig instance
        call_args = mock_evaluate.call_args
        assert call_args.kwargs["run_config"] == mock_runconfig_instance

    @patch("src.ragas_evaluator.evaluate")
    def test_evaluate_exception_handling(self, mock_evaluate, evaluator):
        """Test evaluation with exception."""
        mock_evaluate.side_effect = Exception("Evaluation error")
        
        result = evaluator.evaluate("query", "answer", ["context"])
        
        assert result is None

    def test_format_scores_none(self, evaluator):
        """Test formatting with None scores."""
        result = evaluator.format_scores(None)
        assert result == "No evaluation metrics available."

    def test_format_scores_with_metrics(self, evaluator):
        """Test formatting with metric scores."""
        scores = {
            "faithfulness": 0.9,
            "answer_relevancy": 0.85,
            "context_precision": 0.92,
            "evaluation_time": 2.5,
        }
        
        result = evaluator.format_scores(scores)
        
        assert "faithfulness: 0.9000" in result
        assert "answer_relevancy: 0.8500" in result
        assert "context_precision: 0.9200" in result
        assert "Evaluation Time: 2.50s" in result

    def test_format_scores_empty(self, evaluator):
        """Test formatting with empty scores."""
        result = evaluator.format_scores({})
        assert result == ""
