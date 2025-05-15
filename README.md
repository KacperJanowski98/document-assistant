# Document Assistant: RAG POC for Technical Documents

A Proof of Concept (POC) implementation of a Retrieval-Augmented Generation (RAG) pipeline specifically tailored for querying technical documents, such as communication protocol specifications.

## Project Overview

Technical documents often contain highly structured information (e.g., bit-level descriptions in tables, configuration parameters) that is difficult to query accurately using standard search methods or general-purpose Large Language Models (LLMs). The Document Assistant addresses this challenge by:

1. Processing Markdown documents with a structure-aware approach
2. Using vector embeddings for semantic search
3. Applying a specialized RAG pipeline to generate accurate answers
4. Including automated evaluation metrics using RAGAs framework to measure quality of responses

## Features

- **Modular Architecture**: Clear separation of concerns between document processing, embeddings, retrieval, and generation
- **Markdown Processing**: Specialized chunking to preserve header context
- **Vector Search**: ChromaDB integration for efficient similarity search
- **LLM Integration**: Uses Ollama for local LLM access
- **Automated Evaluation**: RAGAs framework integration for quality metrics
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

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

**Environment Variables Configuration:**

The following environment variables can be configured in your `.env` file:

- **`LANGCHAIN_API_KEY`**: Your LangSmith API key for tracing and monitoring (optional)
  - Get your API key from [LangSmith](https://smith.langchain.com/)
  - If not set, LangSmith tracing will be disabled but the application will work normally
- **`LANGCHAIN_PROJECT`**: Project name for organizing traces in LangSmith (optional)
  - Defaults to: `"document-assistant"`
  - Useful for separating different environments (dev, prod, etc.)
- **`LANGCHAIN_TRACING_V2`**: Enable or disable LangSmith tracing (optional)
  - Set to: `"true"` to enable tracing
  - If not set or set to `"false"`, tracing is disabled

**LangSmith Setup Guide:**

1. Sign up for a free LangSmith account at [smith.langchain.com](https://smith.langchain.com/)
2. Create a new API key in your account settings
3. Add the API key to your `.env` file:
   ```
   LANGCHAIN_API_KEY=your_api_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=document-assistant
   ```
4. Run the application - traces will automatically appear in your LangSmith dashboard

The application will warn you if the API key is not set but will continue to function normally.

5. Install and run Ollama with the required model
```bash
# Follow instructions at https://ollama.ai/ to install Ollama
ollama pull mistral  # or the model specified in config.py
```

## Usage

### Processing Documents

The system accepts documents in Markdown format. You can convert PDF technical documents to Markdown using tools like `docling` or `marker-pdf`. See [PDF-to-Markdown Evaluation](docs/pdf_to_markdown_evaluation.md) for more details.

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

Adjust retrieval size:
```bash
python src/main.py query -q "Your question" -k 10  # Retrieve top 10 chunks
```

### Show Configuration

```bash
python src/main.py config
```

## Query Output

The CLI displays comprehensive information for each query:

1. **Query**: The original user question
2. **Retrieved Context**: The relevant document chunks found
3. **Answer**: The generated response
4. **Retrieval Info**: Statistics about the retrieval process
5. **RAGAS Metrics** (if enabled):
   - **Faithfulness**: How well the answer is grounded in the retrieved context
   - **Answer Relevancy**: How relevant the answer is to the question
   - **Context Precision**: Signal-to-noise ratio of the retrieved context
   - **Evaluation Time**: Time taken for RAGAs evaluation

Example output:
```
====
Query
====

What is the XYZ Protocol?

==================
Retrieved Context
==================

[Header 1 > Header 2]
Context chunk 1...

---

[Header 3 > Header 4]
Context chunk 2...

======
Answer
======

The XYZ Protocol is...

==============
Retrieval Info
==============

Number of chunks retrieved: 5
Similarity scores: min=0.7234, max=0.9123, avg=0.8456

============
RAGAS Metrics
============

  faithfulness: 0.9200
  answer_relevancy: 0.8850
  context_precision: 0.9100
  Evaluation Time: 3.45s

Processing time: 5.23 seconds
```

## Project Structure

```
document-assistant/
├── data/                      # Sample data files
│   └── sample_technical_doc.md
├── docs/                      # Documentation
│   ├── pdf_to_markdown_evaluation.md
│   ├── project_requirements_document.md
│   └── todo.md
├── src/                       # Source code
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── document_processor.py  # Document loading and chunking
│   ├── embedding_manager.py   # Embeddings and vector store
│   ├── llm_generator.py       # LLM interaction and answer generation
│   ├── main.py                # CLI and main entry point
│   ├── rag_pipeline.py        # Core RAG pipeline coordination
│   └── ragas_evaluator.py     # RAGAs evaluation integration
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_document_processor.py
│   ├── test_embedding_manager.py
│   ├── test_llm_generator.py
│   ├── test_main.py           # CLI tests
│   ├── test_rag_pipeline.py
│   ├── test_ragas_evaluator.py
│   └── test_utils.py          # Environment variable tests
├── .env.example               # Example environment variables
├── .gitignore
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── pyproject.toml             # Project dependencies and configuration
├── README.md                  # This file
└── run_checks.py              # Code quality check script
```

## Configuration

The application behavior can be customized through the `src/config.py` file:

### Core Settings
- `OLLAMA_MODEL`: LLM model to use (default: "mistral")
- `OLLAMA_BASE_URL`: Ollama API URL (default: "http://localhost:11434")

### Embedding Settings
- `EMBEDDING_MODEL_PROVIDER`: Provider for embeddings ("huggingface" or "ollama")
- `EMBEDDING_MODEL_NAME`: Model name for embeddings

### Document Processing
- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)

### Retrieval Settings
- `TOP_K_CHUNKS`: Number of chunks to retrieve (default: 5)

### Evaluation Settings
- `ENABLE_RAGAS_EVAL`: Toggle RAGAs evaluation (default: True)

### Prompts
- `SYSTEM_PROMPT`: System instructions for the LLM
- `RAG_PROMPT_TEMPLATE`: Template for constructing prompts

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ragas_evaluator.py

# Run with coverage
pytest --cov=src tests/

# Run tests in verbose mode
pytest -v

# Run tests and show print statements
pytest -s

# Run all checks (tests and linting) with the provided script
python run_checks.py
```

### Test Coverage

The project includes comprehensive unit tests for all major components:
- Configuration loading and environment variable handling
- Document processing and chunking
- Embedding management and vector store operations
- LLM interactions and answer generation
- RAG pipeline coordination
- RAGAs evaluation integration
- CLI functionality and error handling

## Code Quality

### Running Code Quality Checks

```bash
# Run ruff linter
ruff check src/ tests/

# Run ruff formatter
ruff format src/ tests/

# Check formatting without making changes
ruff format --check src/ tests/

# Use the run_checks.py script for all checks in one command
python run_checks.py
```

### Pre-commit Setup

To automatically run code quality checks before committing:

```bash
# Install pre-commit
pip install pre-commit

# Set up pre-commit hooks
pre-commit install
```

This will run the following checks before each commit:
- Ruff linting
- Ruff formatting
- Unit tests
- Trailing whitespace checks
- End-of-file fixer
- YAML validation
- Large file check

## Performance Considerations

- RAGAs evaluation adds computational overhead as it requires additional LLM calls
- You can disable RAGAs evaluation by setting `ENABLE_RAGAS_EVAL = False` in `config.py`
- LangSmith tracing can be disabled by not setting the `LANGCHAIN_API_KEY`

## Troubleshooting

### Common Issues

1. **LangSmith API Key Warning**
   - If you see "Warning: LANGCHAIN_API_KEY not set", this is normal if you haven't configured LangSmith
   - The application will work without LangSmith, just without tracing capabilities

2. **Ollama Connection Issues**
   - Ensure Ollama is running: `ollama serve`
   - Check the model is available: `ollama list`
   - Verify the URL in `config.py` matches your Ollama installation

3. **Environment Variable Issues**
   - Ensure `.env` file exists (copy from `.env.example`)
   - Check that the `.env` file is in the project root directory
   - Verify variables are properly formatted: `KEY=value` (no spaces around `=`)

4. **Dependency Warning**
   - If you see a warning about deprecated Ollama import from LangChain, ignore it - we've updated to the latest version

## Future Enhancements

Planned improvements for future phases:
- Advanced RAGAs metrics with ground truth evaluation
- Reranking algorithms for better retrieval
- Fine-tuning of embeddings and LLMs
- Advanced chunking strategies
- Direct PDF ingestion pipeline
- Web-based user interface
- Batch processing capabilities
- Caching for improved performance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and code quality checks (`python run_checks.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT
