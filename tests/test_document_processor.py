#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the document processor module.
"""
import os
import tempfile
from pathlib import Path

import pytest

from src.document_processor import DocumentProcessor
from src import config


class TestDocumentProcessor:
    """Test the DocumentProcessor class."""

    def test_init_with_defaults(self):
        """Test initializing with default values."""
        processor = DocumentProcessor()
        assert processor.chunk_size == config.CHUNK_SIZE
        assert processor.chunk_overlap == config.CHUNK_OVERLAP

    def test_init_with_custom_values(self):
        """Test initializing with custom values."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100

    def test_load_markdown_file_not_found(self):
        """Test loading a non-existent file."""
        processor = DocumentProcessor()
        with pytest.raises(FileNotFoundError):
            processor.load_markdown("nonexistent_file.md")

    def test_load_markdown(self, sample_markdown_content):
        """Test loading a markdown file."""
        processor = DocumentProcessor()
        
        # Create a temporary file with the sample content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as temp_file:
            temp_file.write(sample_markdown_content)
            temp_file_path = temp_file.name
        
        try:
            # Load the markdown file
            content = processor.load_markdown(temp_file_path)
            
            # Check that the content was loaded correctly
            assert isinstance(content, str)
            assert len(content) > 0
            assert "Sample Technical Document" in content
            assert "Section 1" in content
            assert "Parameter 1: 0x01" in content
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_split_markdown(self, sample_markdown_content):
        """Test splitting markdown content."""
        processor = DocumentProcessor(chunk_size=200, chunk_overlap=50)
        
        # Split the content
        chunks = processor.split_markdown(sample_markdown_content)
        
        # Check that we have chunks
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
        
        # Check metadata
        headers_found = False
        for chunk in chunks:
            metadata = chunk["metadata"]
            if "header_1" in metadata and metadata["header_1"] == "Sample Technical Document":
                headers_found = True
                break
        
        assert headers_found, "Header metadata not properly captured"
        
        # Check content splitting
        content_lengths = [len(chunk["content"]) for chunk in chunks]
        assert all(length <= processor.chunk_size for length in content_lengths), \
            "Chunks exceed maximum size"
