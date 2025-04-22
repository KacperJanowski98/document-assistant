#!/usr/bin/env python
"""
Document processor module for handling document loading and chunking.
"""
from pathlib import Path
from typing import Any

from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader

from src import config


class DocumentProcessor:
    """Class for loading and processing documents."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        """
        Initialize the document processor.

        Args:
            chunk_size: Size of each text chunk.
            chunk_overlap: Overlap between chunks.
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP

    def load_markdown(self, file_path: str) -> str:
        """
        Load content from a markdown file.

        Args:
            file_path: Path to the markdown file.

        Returns:
            The content of the markdown file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Use UnstructuredMarkdownLoader from LangChain for consistent loading
        loader = UnstructuredMarkdownLoader(str(file_path))
        documents = loader.load()
        
        # Combine all document pages into a single text
        return "\n\n".join(doc.page_content for doc in documents)

    def split_markdown(self, markdown_content: str) -> list[dict[str, Any]]:
        """
        Split markdown content into chunks, preserving header context.

        Args:
            markdown_content: Content to split.

        Returns:
            List of document chunks with header metadata.
        """
        # Define headers to extract
        headers_to_split_on = [
            ("#", "header_1"),
            ("##", "header_2"),
            ("###", "header_3"),
            ("####", "header_4"),
        ]

        # First split based on headers
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,
        )
        md_header_splits = markdown_splitter.split_text(markdown_content)

        # Then do a recursive character split on the header-based splits
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        
        final_chunks = []
        
        # Process each header-split document
        for doc in md_header_splits:
            # Extract metadata (headers)
            metadata = doc.metadata.copy()
            
            # Further split by size if needed
            if len(doc.page_content) > self.chunk_size:
                smaller_docs = text_splitter.split_text(doc.page_content)
                for smaller_doc in smaller_docs:
                    final_chunks.append({
                        "content": smaller_doc,
                        "metadata": metadata
                    })
            else:
                final_chunks.append({
                    "content": doc.page_content,
                    "metadata": metadata
                })
        
        return final_chunks
