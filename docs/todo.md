# TODO List: RAG POC for Technical Documents (Phase 1 - v1.0)

## Phase 0: Setup & Pre-processing Evaluation

-   [ ] **Environment Setup:**
    -   [ ] Ensure Python >= 3.10.
    -   [ ] Install `uv`.
    -   [ ] Create/activate venv using `uv`.
    -   [ ] Init Git repo.
    -   [ ] **Create `.gitignore` file and add `.env` and common Python ignores (`__pycache__/`, `.venv/`, etc.).**
-   [ ] **Project Structure:**
    -   [ ] Create dirs (`src/`, `tests/`, etc.).
    -   [ ] Create `src/main.py`, `src/config.py`.
    -   [ ] Init dependency file (`pyproject.toml` or `requirements.txt`).
    -   [ ] **Create `.env.example` file with placeholders for required environment variables (e.g., `LANGCHAIN_API_KEY=YOUR_API_KEY_HERE`).**
-   [ ] **Install Core Dependencies (using `uv`):**
    -   [ ] Install `langchain langchain-community langchain-ollama`.
    -   [ ] Install `ollama` (CLI). Pull LLM model.
    -   [ ] Install `chromadb`.
    -   [ ] Install `pytest`.
    -   [ ] Install `langsmith`.
    -   [ ] Install `ragas`.
    -   [ ] Install `unstructured[md]`.
    -   [ ] Install `sentence-transformers`.
    -   [ ] Install `torch` (if required).
    -   [ ] Install CLI lib (e.g., `click`).
    -   [ ] Install `ruff`.
    -   [ ] **Install `python-dotenv`.**
    -   [ ] Add packages to dependency file.
-   [ ] **Configure Tooling:**
    -   [ ] Configure `ruff`.
-   [ ] **PDF-to-Markdown Tool Evaluation (Manual):**
    -   [ ] Install `docling` & `marker`.
    -   [ ] Get sample PDF.
    -   [ ] Run tools.
    -   [ ] Compare outputs.
    -   [ ] Select input Markdown file(s).

## Phase 1: Configuration & Core RAG Pipeline

-   [ ] **Implement Configuration & Secrets Loading:**
    -   [ ] **In `main.py` (or an initialization module): Add code to load `.env` file using `dotenv.load_dotenv()` *early* in the execution flow.**
    -   [ ] Implement `config.py` with non-sensitive settings (Ollama model, embedding defaults, ChromaDB path, chunking, retrieval, prompts, RAGAs toggle etc.).
    -   [ ] Ensure components requiring API keys (like LangSmith client initialization) read them from environment variables (e.g., `os.getenv("LANGCHAIN_API_KEY")`).
-   [ ] **Implement Document Ingestion:**
    -   [ ] Load Markdown.
    -   [ ] Split document (use config).
    -   [ ] Initialize embedding model (use config).
    -   [ ] Initialize ChromaDB client (use config).
    -   [ ] Create/load ChromaDB collection (use config).
    -   [ ] Embed chunks and add to ChromaDB.
-   [ ] **Implement Retrieval:**
    -   [ ] Create retriever from ChromaDB.
    -   [ ] Configure retriever `k` (use config).
    -   [ ] Implement retrieval & capture scores.
-   [ ] **Implement Generation:**
    -   [ ] Initialize Ollama LLM (use config).
    -   [ ] Create prompt template (use config).
    -   [ ] Build core RAG chain/logic.
    -   [ ] Capture generated answer.

## Phase 2: CLI & Evaluation Integration

-   [ ] **Implement CLI Interface (`main.py`):**
    -   [ ] Use `argparse` or `click` for args.
    -   [ ] **Ensure `.env` loading happens before CLI logic executes.**
    -   [ ] Orchestrate RAG pipeline.
    -   [ ] Handle document ingestion logic.
    -   [ ] Format/print initial output (Query, Context, Answer, Info).
-   [ ] **Integrate RAGAs Evaluation:**
    -   [ ] Import RAGAs components.
    -   [ ] Prepare RAGAs dataset dictionary.
    *   [ ] Implement `ragas.evaluate` call.
    *   [ ] Implement conditional execution (`ENABLE_RAGAS_EVAL`).
    *   [ ] Update CLI output to display RAGAs metrics.

## Phase 3: Observability, Testing & Documentation

-   [ ] **Integrate LangSmith:**
    -   [ ] **Ensure necessary LangSmith env vars (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`) are documented in `.env.example` and loaded.**
    -   [ ] Verify traces in LangSmith UI.
-   [ ] **Implement Unit Tests (`tests/`):**
    -   [ ] Setup `pytest`.
    -   [ ] Write tests covering core logic (Config, Utils, Loading/Splitting, RAG chain w/ mocks, CLI parsing, RAGAs eval w/ mocks). **Test behavior when env vars are present/missing if applicable.**
    -   [ ] Aim for comprehensive coverage.
    -   [ ] Ensure tests run (`pytest`).
-   [ ] **Implement Code Quality Checks:**
    -   [ ] Run `ruff check .` & `ruff format .`.
    -   [ ] Integrate `ruff` into pre-commit hooks (optional).
-   [ ] **Write Documentation:**
    -   [ ] Update `README.md`:
        -   Goal
        -   **Setup:** Python 3.10+, `uv`, dependencies, Ollama, **`.env` file creation from `.env.example` for API keys (esp. LangSmith)**.
        -   Config (`config.py`)
        -   Running (`uv run python src/main.py ...`)
        -   PDF tools note
        -   Output interpretation (incl. RAGAs).

## Phase 4: Review & Refinement

-   [ ] **Code Review**.
-   [ ] **Functionality Check** (including testing with/without LangSmith enabled via env vars).
-   [ ] **Verify Outputs**.
-   [ ] **Check LangSmith**.
-   [ ] **Run Linters/Formatters**.
-   [ ] **Run Tests**.
-   [ ] **Finalize `README.md`**.
-   [ ] **Commit final changes**.