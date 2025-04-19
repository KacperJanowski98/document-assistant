# Document Assistant: RAG POC for Technical Documents

This repository contains a Proof of Concept (POC) implementing a Retrieval-Augmented Generation (RAG) pipeline specifically tailored for querying technical documents.

## Project Overview

The Document Assistant aims to solve the problem of accurately extracting precise details from structured technical documents, which often contain bit-level descriptions, tables, and configuration parameters that are difficult to query using standard search methods or general-purpose Large Language Models (LLMs).

## Setup

### Requirements
- Python >= 3.10
- `uv` package manager
- Ollama (for local LLM access)

### Installation
1. Clone this repository
2. Create a virtual environment using `uv`:
   ```
   uv venv
   source .venv/bin/activate   # On Unix/macOS
   # OR
   .venv\Scripts\activate      # On Windows
   ```
3. Install dependencies:
   ```
   uv pip install -e .
   ```
4. Create a `.env` file based on `.env.example` with your API keys:
   ```
   cp .env.example .env
   # Then edit .env with your actual API keys
   ```
5. Install and run Ollama with the required model:
   ```
   # Follow instructions at https://ollama.ai/ to install Ollama
   ollama pull mistral  # pulls the default model specified in config.py
   ```

### Configuration
The application uses a `config.py` file for all configurable parameters. You can modify this file to change:
- LLM model
- Embedding model
- Chunking parameters
- Retrieval settings
- RAGAs evaluation toggle
- System and RAG prompts

## Usage

Basic usage (once fully implemented):

```
python src/main.py --document path/to/your/document.md --query "Your query here"
```

## PDF to Markdown Conversion

This project requires Markdown documents as input. See [PDF-to-Markdown Evaluation](docs/pdf_to_markdown_evaluation.md) for instructions on converting PDFs to Markdown using `docling` and `marker` tools.

## Project Status

This project is currently in development. See the [todo list](docs/todo.md) for current progress.

## Directory Structure

```
document-assistant/
├── docs/                  # Documentation files
├── src/                   # Source code
│   ├── __init__.py
│   ├── main.py            # Main application entry point
│   └── config.py          # Configuration settings
├── tests/                 # Test files
│   ├── __init__.py
│   ├── conftest.py        # Test fixtures
│   └── test_config.py     # Tests for config module
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── pyproject.toml         # Project dependencies and configuration
└── README.md              # This file
```

## License

MIT
