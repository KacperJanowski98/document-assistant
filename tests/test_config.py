#!/usr/bin/env python
"""
Tests for the config module.
"""
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules for testing
sys.path.append(str(Path(__file__).parent.parent))

from src import config


def test_config_paths() -> None:
    """Test that the config paths are set correctly."""
    assert Path(config.__file__).parent.parent == config.PROJECT_ROOT
    assert config.SRC_DIR == config.PROJECT_ROOT / "src"
    assert config.DATA_DIR == config.PROJECT_ROOT / "data"
    assert config.OUTPUT_DIR == config.PROJECT_ROOT / "output"


def test_get_config_summary() -> None:
    """Test the get_config_summary function."""
    summary = config.get_config_summary()
    assert "ollama_model" in summary
    assert "embedding_model_provider" in summary
    assert "embedding_model_name" in summary
    assert "chunk_size" in summary
    assert "chunk_overlap" in summary
    assert "top_k_chunks" in summary
    assert "enable_ragas_eval" in summary
    
    # Verify the values match the config constants
    assert summary["ollama_model"] == config.OLLAMA_MODEL
    assert summary["embedding_model_provider"] == config.EMBEDDING_MODEL_PROVIDER
    assert summary["embedding_model_name"] == config.EMBEDDING_MODEL_NAME
    assert summary["chunk_size"] == config.CHUNK_SIZE
    assert summary["chunk_overlap"] == config.CHUNK_OVERLAP
    assert summary["top_k_chunks"] == config.TOP_K_CHUNKS
    assert summary["enable_ragas_eval"] == config.ENABLE_RAGAS_EVAL
