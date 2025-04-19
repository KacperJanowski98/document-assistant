#!/usr/bin/env python
"""
Main module for the document assistant application.
"""
import os
import sys
from pathlib import Path

import dotenv

# Add the src directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
dotenv.load_dotenv()


def main():  # noqa: ANN201
    """Main entry point for the application."""
    print("Document Assistant - RAG POC for Technical Documents")
    print("Environment setup successful!")
    
    # Check if required environment variables are set
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
    if not langchain_api_key:
        print("Warning: LANGCHAIN_API_KEY not set. LangSmith tracing will not be available.")
    
    # Further implementation will be added in Phase 1 and 2


if __name__ == "__main__":
    main()
