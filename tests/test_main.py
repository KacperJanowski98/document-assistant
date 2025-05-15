"""
Tests for the main CLI module.
"""
import os
from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path

from src.main import main, print_section_header, print_retrieval_info, print_ragas_metrics, format_output


class TestCLIFunctions:
    """Test the CLI helper functions."""

    def test_print_section_header(self, capsys):
        """Test printing section headers."""
        print_section_header("Test Header", "=")
        captured = capsys.readouterr()
        assert "============\n" in captured.out
        assert "Test Header\n" in captured.out
        assert "============\n" in captured.out

    def test_print_retrieval_info(self, capsys):
        """Test printing retrieval information."""
        info = {
            "chunk_count": 5,
            "score_stats": {
                "min_score": 0.7234,
                "max_score": 0.9123,
                "avg_score": 0.8456
            }
        }
        print_retrieval_info(info)
        captured = capsys.readouterr()
        assert "Number of chunks retrieved: 5" in captured.out
        assert "Similarity scores: min=0.7234" in captured.out
        assert "max=0.9123" in captured.out
        assert "avg=0.8456" in captured.out

    @patch('src.main.RAGASEvaluator')
    def test_print_ragas_metrics(self, mock_evaluator, capsys):
        """Test printing RAGAS metrics."""
        mock_evaluator_instance = MagicMock()
        mock_evaluator.return_value = mock_evaluator_instance
        mock_evaluator_instance.format_scores.return_value = "Formatted RAGAS scores"
        
        metrics = {
            "faithfulness": 0.92,
            "answer_relevancy": 0.88,
            "context_precision": 0.91
        }
        
        print_ragas_metrics(metrics)
        captured = capsys.readouterr()
        
        assert "RAGAS Metrics" in captured.out
        assert "Formatted RAGAS scores" in captured.out

    def test_format_output(self, capsys):
        """Test formatting complete output."""
        result = {
            "query": "Test query",
            "context": "Test context",
            "answer": "Test answer",
            "retrieval_info": {
                "chunk_count": 3,
                "score_stats": {
                    "min_score": 0.8,
                    "max_score": 0.95,
                    "avg_score": 0.875
                }
            },
            "ragas_metrics": {
                "faithfulness": 0.9,
                "answer_relevancy": 0.85
            },
            "metadata": {
                "processing_time": "2.5 seconds"
            }
        }
        
        with patch('src.main.print_ragas_metrics') as mock_print_ragas:
            format_output(result)
            captured = capsys.readouterr()
            
            assert "Test query" in captured.out
            assert "Test context" in captured.out
            assert "Test answer" in captured.out
            assert "Processing time: 2.5 seconds" in captured.out
            
            # Verify print_ragas_metrics was called
            mock_print_ragas.assert_called_once_with(result["ragas_metrics"])


class TestCLIMain:
    """Test the main CLI functionality."""

    @patch('src.main.RAGPipeline')
    @patch('src.main.argparse.ArgumentParser')
    def test_main_without_langchain_api_key(self, mock_parser, mock_pipeline, capsys):
        """Test main when LANGCHAIN_API_KEY is not set."""
        # Mock argparse
        mock_args = MagicMock()
        mock_args.command = "config"
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.return_value = mock_args
        
        # Clear environment variable
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.main.get_config') as mock_get_config:
                main()
                
                captured = capsys.readouterr()
                assert "Warning: LANGCHAIN_API_KEY not set" in captured.out

    @patch('src.main.RAGPipeline')
    @patch('src.main.argparse.ArgumentParser')
    def test_main_with_langchain_api_key(self, mock_parser, mock_pipeline, capsys):
        """Test main when LANGCHAIN_API_KEY is set."""
        # Mock argparse
        mock_args = MagicMock()
        mock_args.command = "config"
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.return_value = mock_args
        
        # Set environment variable
        with patch.dict(os.environ, {"LANGCHAIN_API_KEY": "test_key"}):
            with patch('src.main.get_config') as mock_get_config:
                main()
                
                captured = capsys.readouterr()
                assert "Warning: LANGCHAIN_API_KEY not set" not in captured.out

    @patch('src.main.RAGPipeline')
    @patch('src.main.argparse.ArgumentParser')
    def test_main_ingest_command(self, mock_parser, mock_pipeline):
        """Test main with ingest command."""
        # Mock argparse
        mock_args = MagicMock()
        mock_args.command = "ingest"
        mock_args.document = "test.md"
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.return_value = mock_args
        
        # Mock pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        with patch.dict(os.environ, {"LANGCHAIN_API_KEY": "test_key"}):
            main()
            
            # Verify ingest was called
            mock_pipeline_instance.ingest_document.assert_called_once_with("test.md")

    @patch('src.main.RAGPipeline')
    @patch('src.main.argparse.ArgumentParser')
    def test_main_query_command(self, mock_parser, mock_pipeline):
        """Test main with query command."""
        # Mock argparse
        mock_args = MagicMock()
        mock_args.command = "query"
        mock_args.query = "Test query"
        mock_args.document = None
        mock_args.top_k = 5
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.return_value = mock_args
        
        # Mock pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_pipeline_instance.query.return_value = {
            "query": "Test query",
            "context": "Test context",
            "answer": "Test answer"
        }
        
        with patch.dict(os.environ, {"LANGCHAIN_API_KEY": "test_key"}):
            with patch('src.main.format_output') as mock_format:
                main()
                
                # Verify query was called
                mock_pipeline_instance.query.assert_called_once_with("Test query", top_k=5)
                mock_format.assert_called_once()
