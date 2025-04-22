#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module for the document assistant application.
"""
import os
import sys
import argparse
from pathlib import Path
import json
import dotenv
import pprint

# Add the src directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
dotenv.load_dotenv()

from src.rag_pipeline import RAGPipeline
from src import config


def print_section_header(title, char="="):
    """Print a section header."""
    header = char * len(title)
    print(f"\n{header}")
    print(title)
    print(f"{header}\n")


def print_retrieval_info(info):
    """Format and print retrieval information."""
    print_section_header("Retrieval Info", "-")
    print(f"Number of chunks retrieved: {info['chunk_count']}")
    
    if 'score_stats' in info and info['score_stats']:
        score_stats = info['score_stats']
        print(f"Similarity scores: min={score_stats.get('min_score', 'N/A'):.4f}, "
              f"max={score_stats.get('max_score', 'N/A'):.4f}, "
              f"avg={score_stats.get('avg_score', 'N/A'):.4f}")


def format_output(result):
    """Format the query result for display."""
    # Print the query
    print_section_header("Query")
    print(result["query"])
    
    # Print the retrieved context
    print_section_header("Retrieved Context")
    print(result["context"])
    
    # Print the answer
    print_section_header("Answer")
    print(result["answer"])
    
    # Print retrieval information
    if "retrieval_info" in result:
        print_retrieval_info(result["retrieval_info"])  # Pass the retrieval_info part, not the entire result
    
    # Print processing time if available
    if "metadata" in result and "processing_time" in result["metadata"]:
        print(f"\nProcessing time: {result['metadata']['processing_time']}")


def ingest_document(args):
    """Ingest a document into the vector store."""
    pipeline = RAGPipeline()
    pipeline.ingest_document(args.document)
    print(f"Document '{args.document}' successfully ingested.")


def query_document(args):
    """Query the document assistant."""
    pipeline = RAGPipeline()
    
    # Check if a query string was provided
    if args.query:
        result = pipeline.query(args.query, top_k=args.top_k)
        format_output(result)
    else:
        # Interactive mode
        print("Document Assistant - Interactive Mode")
        print("Enter 'exit', 'quit', or Ctrl+C to exit.")
        
        while True:
            try:
                user_query = input("\nEnter your query: ")
                if user_query.lower() in ["exit", "quit"]:
                    break
                
                result = pipeline.query(user_query, top_k=args.top_k)
                format_output(result)
            
            except KeyboardInterrupt:
                print("\nExiting interactive mode.")
                break


def get_config(args):
    """Print the current configuration."""
    print_section_header("Current Configuration")
    pprint.pprint(config.get_config_summary())


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Document Assistant - RAG POC for Technical Documents")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a document")
    ingest_parser.add_argument("document", help="Path to the document to ingest")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the document assistant")
    query_parser.add_argument("-d", "--document", help="Path to the document to query (will ingest first)")
    query_parser.add_argument("-q", "--query", help="Query string")
    query_parser.add_argument("-k", "--top-k", type=int, default=config.TOP_K_CHUNKS,
                           help=f"Number of chunks to retrieve (default: {config.TOP_K_CHUNKS})")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show current configuration")
    
    args = parser.parse_args()
    
    # Check for LangSmith configuration
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
    if not langchain_api_key:
        print("Warning: LANGCHAIN_API_KEY not set. LangSmith tracing will not be available.")
    
    # Execute the appropriate command
    if args.command == "ingest":
        ingest_document(args)
    elif args.command == "query":
        # If a document is specified, ingest it first
        if args.document:
            ingest_document(args)
        query_document(args)
    elif args.command == "config":
        get_config(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
