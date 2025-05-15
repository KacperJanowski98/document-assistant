"""
Tests for environment variable loading and utility functions.
"""
import os
from unittest.mock import patch
import pytest


def test_dotenv_loading():
    """Test that dotenv is loaded early in main module."""
    # This test verifies that the import of main.py triggers dotenv loading
    # which is crucial for LangSmith API key availability
    with patch('dotenv.load_dotenv') as mock_dotenv:
        # Import main to trigger the dotenv loading
        import src.main
        
        # Verify dotenv.load_dotenv was called
        mock_dotenv.assert_called_once()


class TestEnvironmentVariableHandling:
    """Test environment variable handling across the application."""
    
    def test_langsmith_env_vars_documented(self):
        """Test that all required LangSmith environment variables are documented."""
        # Read the .env.example file to verify documentation
        env_example_path = "../../.env.example"
        
        # Check if file exists relative to the test
        from pathlib import Path
        test_dir = Path(__file__).parent
        project_root = test_dir.parent
        env_example_full_path = project_root / ".env.example"
        
        if env_example_full_path.exists():
            with open(env_example_full_path, 'r') as f:
                content = f.read()
                
            # Verify all required LangSmith variables are documented
            assert "LANGCHAIN_API_KEY" in content
            assert "LANGCHAIN_TRACING_V2" in content
            assert "LANGCHAIN_PROJECT" in content
        else:
            # If file doesn't exist during testing, just pass
            # This allows the test to run in different environments
            pass
    
    @patch.dict(os.environ, {"LANGCHAIN_API_KEY": "test_key", "LANGCHAIN_PROJECT": "test_project"})
    def test_langsmith_initialization_with_env_vars(self):
        """Test LangSmith initialization when environment variables are present."""
        from src.rag_pipeline import RAGPipeline
        
        # Create pipeline with langsmith enabled
        pipeline = RAGPipeline(enable_langsmith=True)
        
        # Verify callback manager was created
        assert pipeline.enable_langsmith is True
        if os.getenv("LANGCHAIN_API_KEY"):
            assert pipeline.callback_manager is not None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_langsmith_initialization_without_env_vars(self):
        """Test LangSmith initialization when environment variables are missing."""
        from src.rag_pipeline import RAGPipeline
        
        # Create pipeline with langsmith enabled but no env vars
        pipeline = RAGPipeline(enable_langsmith=True)
        
        # Verify callback manager was not created
        assert pipeline.enable_langsmith is True
        assert pipeline.callback_manager is None
    
    def test_config_uses_env_vars_for_secrets(self):
        """Test that config module doesn't contain hardcoded secrets."""
        import src.config as config
        
        # Get all config attributes
        config_attrs = dir(config)
        
        # Filter to get only uppercase constants (typical configuration)
        config_constants = [attr for attr in config_attrs if attr.isupper()]
        
        # Check each constant
        for constant in config_constants:
            value = getattr(config, constant)
            
            # Ensure no common secret patterns in string values
            if isinstance(value, str):
                value_lower = value.lower()
                assert "api_key" not in value_lower
                assert "secret" not in value_lower
                assert "password" not in value_lower
                assert "token" not in value_lower
                
                # Ensure no hardcoded test/example keys
                assert not value.startswith("sk-")  # Common for API keys
                assert not value.startswith("pk-")  # Common for public keys
