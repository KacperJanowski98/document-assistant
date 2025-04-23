# Document Assistant: RAG POC for Technical Documents

A Proof of Concept (POC) implementation of a Retrieval-Augmented Generation (RAG) pipeline specifically tailored for querying technical documents, such as communication protocol specifications.

## Project Overview

Technical documents often contain highly structured information (e.g., bit-level descriptions in tables, configuration parameters) that is difficult to query accurately using standard search methods or general-purpose Large Language Models (LLMs). The Document Assistant addresses this challenge by:

1. Processing Markdown documents with a structure-aware approach
2. Using vector embeddings for semantic search
3. Applying a specialized RAG pipeline to generate accurate answers
4. Including evaluation metrics to measure the quality of responses

## Features

- **Modular Architecture**: Clear separation of concerns between document processing, embeddings, retrieval, and generation
- **Markdown Processing**: Specialized chunking to preserve header context
- **Vector Search**: ChromaDB integration for efficient similarity search
- **LLM Integration**: Uses Ollama for local LLM access
- **Observability**: LangSmith integration for tracing and monitoring (if API key is provided)
- **Command Line Interface**: Easy-to-use CLI with options for document ingestion and querying

## Installation

### Requirements
- Python >= 3.10
- Ollama (for local LLM access)
- UV package manager (recommended) or pip

### Setup Steps

1. Clone this repository
```bash
git clone https://github.com/KacperJanowski98/document-assistant.git
cd document-assistant
```

2. Create and activate a virtual environment
```bash
# Using UV
uv venv
source .venv/bin/activate   # On Unix/macOS
# OR
.venv\Scripts\activate      # On Windows

# Using standard venv
python -m venv .venv
source .venv/bin/activate   # On Unix/macOS
# OR
.venv\Scripts\activate      # On Windows
```

3. Install dependencies
```bash
# Using UV
uv pip install -e .

# Using pip
pip install -e .
```

4. Set up environment variables (optional, for LangSmith integration)
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

5. Install and run Ollama with the required model
```bash
# Follow instructions at https://ollama.ai/ to install Ollama
ollama pull mistral  # pulls the default model specified in config.py
```

## Usage

### Processing Documents

The system accepts documents in Markdown format. You can convert PDF technical documents to Markdown using tools like `docling` or `marker`. See [PDF-to-Markdown Evaluation](docs/pdf_to_markdown_evaluation.md) for more details.

### Ingesting a Document

```bash
python src/main.py ingest data/sample_technical_doc.md
```

### Querying

Single query mode:
```bash
python src/main.py query -q "What is the frame structure of XYZ Protocol?"
```

Interactive mode:
```bash
python src/main.py query
```

Combined ingest and query:
```bash
python src/main.py query -d data/sample_technical_doc.md -q "What is the frame structure of XYZ Protocol?"
```

### Show Configuration

```bash
python src/main.py config
```

## Project Structure

```
document-assistant/
├── data/                  # Sample data files
│   └── sample_technical_doc.md
├── docs/                  # Documentation
│   ├── pdf_to_markdown_evaluation.md
│   ├── project_requirements_document.md
│   └── todo.md
├── src/                   # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── document_processor.py  # Document loading and chunking
│   ├── embedding_manager.py   # Embeddings and vector store
│   ├── llm_generator.py       # LLM interaction and answer generation
│   ├── main.py                # CLI and main entry point
│   └── rag_pipeline.py        # Core RAG pipeline coordination
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_document_processor.py
│   ├── test_embedding_manager.py
│   ├── test_llm_generator.py
│   └── test_rag_pipeline.py
├── .env.example           # Example environment variables
├── .gitignore
├── pyproject.toml         # Project dependencies and configuration
└── README.md              # This file
```

## Configuration

The application behavior can be customized through the `src/config.py` file, including:

- LLM model selection
- Embedding model provider and name
- Document chunking parameters
- ChromaDB settings
- Retrieval settings
- System prompt and RAG prompt template

## Running Tests

```bash
# Install pytest if not included in your dependencies
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest tests/test_document_processor.py
```

## Future Enhancements

Planned improvements for future phases:
- RAGAs evaluation metrics integration
- Reranking algorithms for better retrieval
- Fine-tuning of embeddings and LLMs
- Advanced chunking strategies
- Direct PDF ingestion pipeline
- Web-based user interface

## License

MIT
