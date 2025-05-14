# TODO List: RAG POC for Technical Documents (Phase 1 - v1.0)

## Phase 0: Setup & Pre-processing Evaluation

-   [x] **Environment Setup:**
    -   [x] Ensure Python >= 3.10.
    -   [x] Install `uv`.
    -   [x] Create/activate venv using `uv`.
    -   [x] Init Git repo.
    -   [x] **Create `.gitignore` file and add `.env` and common Python ignores (`__pycache__/`, `.venv/`, etc.).**
-   [x] **Project Structure:**
    -   [x] Create dirs (`src/`, `tests/`, etc.).
    -   [x] Create `src/main.py`, `src/config.py`.
    -   [x] Init dependency file (`pyproject.toml` or `requirements.txt`).
    -   [x] **Create `.env.example` file with placeholders for required environment variables (e.g., `LANGCHAIN_API_KEY=YOUR_API_KEY_HERE`).**
-   [x] **Install Core Dependencies (using `uv`):**
    -   [x] Install `langchain langchain-community langchain-ollama`.
    -   [x] Install `ollama` (CLI). Pull LLM model.
    -   [x] Install `chromadb`.
    -   [x] Install `pytest`.
    -   [x] Install `langsmith`.
    -   [x] Install `ragas`.
    -   [x] Install `unstructured[md]`.
    -   [x] Install `sentence-transformers`.
    -   [x] Install `torch` (if required).
    -   [x] Install CLI lib (e.g., `click`).
    -   [x] Install `ruff`.
    -   [x] **Install `python-dotenv`.**
    -   [x] Add packages to dependency file.
-   [x] **Configure Tooling:**
    -   [x] Configure `ruff`.
-   [x] **PDF-to-Markdown Tool Evaluation (Manual):**
    -   [x] Install `docling` & `marker`.
    -   [ ] Get sample PDF.
    -   [ ] Run tools.
    -   [ ] Compare outputs.
    -   [ ] Select input Markdown file(s).

## Phase 1: Configuration & Core RAG Pipeline

-   [x] **Implement Configuration & Secrets Loading:**
    -   [x] **In `main.py` (or an initialization module): Add code to load `.env` file using `dotenv.load_dotenv()` *early* in the execution flow.**
    -   [x] Implement `config.py` with non-sensitive settings (Ollama model, embedding defaults, ChromaDB path, chunking, retrieval, prompts, RAGAs toggle etc.).
    -   [x] Ensure components requiring API keys (like LangSmith client initialization) read them from environment variables (e.g., `os.getenv("LANGCHAIN_API_KEY")`).
-   [x] **Implement Document Ingestion:**
    -   [x] Load Markdown.
    -   [x] Split document (use config).
    -   [x] Initialize embedding model (use config).
    -   [x] Initialize ChromaDB client (use config).
    -   [x] Create/load ChromaDB collection (use config).
    -   [x] Embed chunks and add to ChromaDB.
-   [x] **Implement Retrieval:**
    -   [x] Create retriever from ChromaDB.
    -   [x] Configure retriever `k` (use config).
    -   [x] Implement retrieval & capture scores.
-   [x] **Implement Generation:**
    -   [x] Initialize Ollama LLM (use config).
    -   [x] Create prompt template (use config).
    -   [x] Build core RAG chain/logic.
    -   [x] Capture generated answer.

## Phase 2: CLI & Evaluation Integration

-   [x] **Implement CLI Interface (`main.py`):**
    -   [x] Use `argparse` or `click` for args.
    -   [x] **Ensure `.env` loading happens before CLI logic executes.**
    -   [x] Orchestrate RAG pipeline.
    -   [x] Handle document ingestion logic.
    -   [x] Format/print initial output (Query, Context, Answer, Info).
-   [x] **Integrate RAGAs Evaluation:**
    -   [x] Import RAGAs components.
    -   [x] Prepare RAGAs dataset dictionary.
    -   [x] Implement `ragas.evaluate` call.
    -   [x] Implement conditional execution (`ENABLE_RAGAS_EVAL`).
    -   [x] Update CLI output to display RAGAs metrics.

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