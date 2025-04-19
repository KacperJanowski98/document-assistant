# Project Requirements Document (PRD): RAG POC for Technical Documents

*   **Version:** 1.0
*   **Date:** 2024-02-29
*   **Status:** Final Draft (for Phase 1)
*   **Author:** AI Assistant (based on user input)
*   **Project Owner:** Kacper Janowski

## 1. Introduction

### 1.1. Problem Statement
Technical documents, especially communication protocol specifications, contain highly structured information (e.g., bit-level descriptions in tables, configuration parameters) that is often difficult to query accurately using standard search methods or general-purpose Large Language Models (LLMs). Extracting precise details requires understanding the document's structure and context. Standard PDF parsing often loses crucial layout information.

### 1.2. Proposed Solution
Develop a Proof of Concept (POC) implementing a basic Retrieval-Augmented Generation (RAG) pipeline specifically tailored for querying technical documents. This POC will ingest documents pre-processed into Markdown format to potentially preserve better structural information. The project will involve evaluating tools (`docling`, `marker`) for converting source PDFs into this target Markdown format. Automated evaluation metrics will be implemented using the RAGAs framework (focusing on ground-truth-free metrics). The system will use a local LLM accessible via Ollama and be operated via a CLI.

### 1.3. Purpose of this Document
This document outlines the requirements for the initial phase (Phase 1) of the RAG POC project. It defines the scope, features, technical stack, evaluation approach (including RAGAs metrics), and monitoring strategy. This serves as a foundation for iterative development and testing of different RAG configurations and pre-processing techniques.

## 2. Goals & Objectives

*   **Goal 1:** Implement a functional, minimal RAG pipeline using Python that ingests Markdown (`.md`) documents.
*   **Goal 2:** Integrate the pipeline with a local LLM accessible via Ollama, configurable via a Python config file (`config.py`).
*   **Goal 3:** Enable querying of a sample technical document (in Markdown format) through a simple Command Line Interface (CLI), displaying the query, retrieved context, answer, retrieval info, and **RAGAs metrics**.
*   **Goal 4:** Establish basic unit testing using `pytest`.
*   **Goal 5:** Integrate observability using LangSmith for tracing RAG and evaluation steps.
*   **Goal 6:** Create a baseline RAG system against which future improvements (like reranking) can be measured.
*   **Goal 7:** Evaluate and compare the effectiveness of `docling` and `marker` libraries for converting source technical PDFs into structured Markdown suitable for RAG ingestion (as a preliminary step).
*   **Goal 8:** Implement automated calculation and display of RAG quality indicators using the **RAGAs** framework, specifically focusing on its ground-truth-free metrics (e.g., `faithfulness`, `answer_relevancy`, `context_precision`).

## 3. Scope

### 3.1. In Scope (Phase 1)

*   **Document Input:** Processing a single technical document provided as a local file in **Markdown (`.md`) format**.
*   **Document Pre-processing Evaluation:** Using `docling` and `marker` libraries to convert sample technical PDF documents into Markdown format. Manual, qualitative comparison of the output. (This conversion process might initially be run manually, separate from the RAG CLI).
*   **Document Processing (RAG Pipeline):** Basic, naive document splitting of the Markdown input (e.g., Markdown-aware splitting or fixed-size chunks).
*   **Configuration:** Using an external Python configuration file (`config.py`) to manage key pipeline parameters, embedding models, chunking settings, retrieval settings, Ollama model, system prompt, and RAG prompt template.
*   **Embeddings:** Generating embeddings using a standard model (provider and identifier specified in `config.py`, e.g., `OllamaEmbeddings`, `HuggingFaceEmbeddings`).
*   **Vector Store:** Using **ChromaDB** as the vector store implementation, configured via `config.py` (allowing persistence).
*   **Retrieval:** Basic similarity search (e.g., top-k retrieved chunks, 'k' configurable). **Log similarity scores of retrieved documents.**
*   **Generation:** Using an LLM served by Ollama (model specified in `config.py`) and using the System Prompt and RAG Prompt Template defined in `config.py`.
*   **Interface:** A basic CLI accepting a Markdown document path and a query. The CLI MUST output the query, retrieved context chunks, the final generated answer, basic retrieval info (scores, count), and **results from selected RAGAs metrics**.
*   **Automated Quality Indicators:**
    *   **Integrate the RAGAs library** to calculate and display/log metrics.
    *   Implement calculation for **at least the following ground-truth-free RAGAs metrics:**
        *   `faithfulness` (Answer groundedness in context)
        *   `answer_relevancy` (Answer relevance to the query)
        *   `context_precision` (Signal-to-noise ratio in retrieved context relevance to the query)
    *   *(Optionally explore `context_relevancy` as an alternative/addition to `context_precision`)*.
*   **Testing:** Unit tests (`pytest`) for core functions.
*   **Monitoring:** Basic tracing of RAG pipeline and evaluation calls using LangSmith.
*   **Code Structure:** A simple Python project structure, runnable directly without compilation. Includes a sample `config.py`.

### 3.2. Out of Scope (Phase 1)

*   **Ground-truth based evaluation:** Metrics requiring pre-defined Q&A pairs or ideal context passages.
*   **RAGAs metrics requiring ground truth:** Specifically `context_recall`, `answer_correctness`, `answer_similarity` are out of scope for Phase 1 calculation.
*   Implementing Reranking functionality (targeted for Phase 2).
*   Direct PDF ingestion into the RAG runtime pipeline (pipeline consumes pre-converted Markdown).
*   Advanced document parsing beyond `docling`/`marker` or basic Markdown splitting.
*   Sophisticated chunking strategies.
*   Fine-tuning embedding models or LLMs.
*   Advanced retrieval techniques (e.g., query expansion, hybrid search).
*   Complex prompt engineering beyond initial templates in `config.py`.
*   Handling multiple documents simultaneously or document collections.
*   User authentication or management.
*   Graphical User Interface (GUI).
*   Deployment to cloud or production environments.

## 4. Target Audience

*   The primary user of this POC is the project developers for testing and experimentation purposes.

## 5. Functional Requirements

*   **FR0:** (Pre-requisite Task) The developer MUST be able to run `docling` and `marker` separately to convert a sample PDF technical document into Markdown format.
*   **FR1:** The RAG system CLI MUST allow the user to specify the path to a local Markdown (`.md`) technical document file.
*   **FR2:** The system MUST load and process the specified Markdown document into text chunks, using chunking parameters (size, overlap) defined as variables in `config.py`.
*   **FR3:** The system MUST generate vector embeddings for the text chunks using the embedding model specified as a variable in `config.py`.
*   **FR4:** The system MUST store the text chunks and their embeddings in ChromaDB, using settings (like collection name or persistence path) from variables in `config.py`.
*   **FR5:** The system MUST allow the user to input a natural language query via the CLI.
*   **FR6:** The system MUST retrieve relevant text chunks from the ChromaDB vector store based on the user's query, potentially using the number of chunks 'k' defined in `config.py`. The system MUST capture the similarity scores associated with each retrieved chunk.
*   **FR7:** The system MUST construct the final prompt for the LLM using the System Prompt and RAG Prompt Template defined as string variables in `config.py`, incorporating the retrieved context and the user's query.
*   **FR8:** The system MUST use the constructed prompt to generate an answer using the Ollama LLM specified as a variable in `config.py`.
*   **FR9:** The system MUST display the following information clearly formatted on the CLI:
    *   The original user query.
    *   A section explicitly labelled "Retrieved Context" containing the text content of the chunks retrieved in FR6.
    *   The final generated answer from FR8, labelled clearly (e.g., "Answer:").
    *   A section labelled "Info:" containing:
        *   Number of context chunks retrieved.
        *   Min/Max/Average similarity scores of retrieved chunks.
        *   *(Optional: Add processing time if straightforwardly measurable)*
    *   A section labelled **"RAGAs Metrics:"** displaying the calculated scores for (at minimum):
        *   `faithfulness`
        *   `answer_relevancy`
        *   `context_precision`
*   **FR10:** The system **MUST** implement the logic for calculating the selected **RAGAs metrics** using the `ragas` library. This will likely involve additional LLM calls orchestrated by RAGAs and instrumented via LangChain/LangSmith.
*   **FR11:** All interactions involving LangChain components (RAG pipeline, **RAGAs evaluation calls**) MUST be traced and logged to LangSmith when configured.
*   **FR12:** The system MUST load its operational parameters and prompts by importing the `config.py` file at startup.
*   **FR13:** The system SHOULD provide sensible default values within `config.py` itself, clearly commented.
*   **FR14:** The `config.py` file MUST be included with the project source code, containing example values for all configurable parameters and prompts.

## 6. Non-Functional Requirements

*   NFR1: Usability
*   NFR2: Testability (Comprehensive coverage)
*   NFR3: Modularity
*   NFR4: Observability (LangSmith)
*   NFR5: Simplicity
*   NFR6: Reproducibility (Conversion)
*   NFR7: Configuration Management (`config.py`)
*   NFR8: Flexibility
*   NFR9: Performance (RAGAs toggle)
*   NFR10: Code Quality (`ruff`)
*   **NFR11: Security:** Sensitive information like API keys (e.g., `LANGCHAIN_API_KEY`) **MUST NOT** be hardcoded or committed to version control. They **MUST** be managed using environment variables, preferably loaded from a `.env` file which is excluded from Git via `.gitignore`.

## 7. Technical Requirements & Architecture

*   **Programming Language:** Python >= 3.10
*   **Package Manager:** `uv`
*   **Code Quality Tooling:** `ruff`
*   **Configuration:** Python file (`config.py`) imported directly. Contains variables for models, paths, parameters, prompts.
*   **Secrets Management:**
    *   Use environment variables for sensitive data (e.g., API keys).
    *   **Recommend using a `.env` file** at the project root to store these variables locally.
    *   **Use a library like `python-dotenv`** to load variables from the `.env` file into the environment upon application startup.
    *   Ensure `.env` file is listed in `.gitignore`.
*   **LLM:** A model served locally via Ollama (identifier specified in `config.py`, e.g., `mistral`).
*   **PDF-to-Markdown Conversion Tools:** `docling`, `marker-pdf` (for external evaluation phase). Requires own installation potentially separate environment.
*   **Core Framework:** LangChain (`langchain`, `langchain-community`, `langchain-ollama`).
*   **Document Loading (Markdown):** LangChain document loaders (e.g., `UnstructuredMarkdownLoader`).
*   **Text Splitting:** LangChain text splitters (e.g., `MarkdownHeaderTextSplitter`), parameters via `config.py`.
*   **Embeddings:** LangChain embedding integrations.
    *   **Default Provider (Configurable):** `huggingface` via `langchain-community` (using `HuggingFaceEmbeddings`).
    *   **Default Model (Configurable):** `sentence-transformers/all-mpnet-base-v2` specified in `config.py`.
    *   *(Option to use `OllamaEmbeddings` by changing config)*.
*   **Vector Store:** LangChain vector store integration with **ChromaDB** (`chromadb`, `langchain-community`), configuration via `config.py`.
*   **Evaluation Framework:** **`ragas`** library.
*   **Testing Framework:** `pytest`.
*   **Monitoring:** `langsmith-sdk` (**requires `LANGCHAIN_API_KEY` and other LangSmith variables set in the environment, typically loaded via `.env`**).
*   **Interface:** Standard Python CLI libraries (e.g., `argparse`, `click`).
*   **Environment:** Standard Python virtual environment managed via `uv`.

## 8. Data Requirements

*   **Input Data (Source):** At least one sample technical document in PDF format suitable for testing `docling` and `marker`.
*   **Input Data (RAG Pipeline):** The Markdown (`.md`) output generated by applying `docling` and/or `marker` to the source PDF.
*   **Test Data (Manual Eval):** A small set (5-10) of Question/Answer pairs derived *manually* from the sample document. The evaluator should know the ideal answer and source location for qualitative assessment. No ground-truth dataset needed for RAGAs metrics in Phase 1.

## 9. Evaluation & Correctness Indicators (Phase 1)

*   **Evaluation Area 1: PDF-to-Markdown Conversion**
    *   **Method:** Manual, qualitative review of the Markdown files generated by `docling` and `marker`.
    *   **Criteria:** Accuracy, table structure preservation, readability, suitability for RAG.
*   **Evaluation Area 2: RAG Pipeline Performance**
    *   **Method 1: Automated RAGAs Metrics:** Run Q&A pairs. Analyze the `faithfulness`, `answer_relevancy`, and `context_precision` scores reported by RAGAs in the CLI output. Log these scores for comparison across runs/configurations.
    *   **Method 2: Manual Qualitative Assessment:** Review CLI output (Query, Context, Answer) alongside the RAGAs scores. Use evaluator knowledge to:
        *   Corroborate RAGAs scores (e.g., does a low `faithfulness` score correspond to a visibly hallucinated answer?).
        *   Assess aspects not fully captured by the selected RAGAs metrics (e.g., overall tone, deeper correctness beyond simple relevance/faithfulness).
    *   **Method 3: LangSmith Trace Review:** Deep dive into traces for the RAG chain and the multiple LLM calls made *by* RAGAs during evaluation. Essential for debugging RAGAs results and understanding latency.
*   **Metrics (Phase 1):**
    *   **Displayed on CLI & Logged (Automated):**
        *   Number of retrieved chunks.
        *   Retrieval similarity scores (min/max/avg).
        *   **RAGAs `faithfulness` score.**
        *   **RAGAs `answer_relevancy` score.**
        *   **RAGAs `context_precision` score.**
    *   **Assessed Manually/Qualitatively:** Overall Answer/Context Quality (using RAGAs scores as primary quantitative input).
    *   **Observed via LangSmith:** Latency (overall and per-component, including RAGAs), detailed prompts/outputs, errors.
*   **Foundation for Reranking:** RAGAs `context_precision` (and retrieval similarity scores) provides a measurable baseline for evaluating future reranking effectiveness.

## 10. Monitoring & Observability

*   **Tool:** LangSmith will be used as the primary monitoring and observability tool for detailed tracing. Crucial for observing the multiple LLM interactions within the RAGAs evaluation process.
*   **Setup:** Requires standard LangSmith environment variables (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`).
*   **Usage:** Manual review of traces in the LangSmith UI to debug, understand performance, and verify intermediate steps.

## 11. Future Considerations (Beyond Phase 1)

*   Implement **reranking** algorithms and evaluate their impact using RAGAs `context_precision` and potentially other metrics.
*   Implement **more RAGAs metrics**, especially if a ground-truth dataset is created (e.g., `answer_correctness`, `context_recall`).
*   Fine-tune the **LLM used for RAGAs evaluation** or experiment with different models.
*   Explore methods to **optimize RAGAs evaluation performance** (e.g., batching, sampling).
*   Explore and implement **advanced chunking strategies** suitable for Markdown/technical docs.
*   Investigate **advanced retrieval techniques** (hybrid search, query transformations).
*   Refine **prompt engineering** based on observations.
*   Automate the **PDF-to-Markdown conversion** step within the pipeline using the preferred tool (`docling` or `marker`).
*   Compare performance with **different embedding models and vector stores**.
*   Add **more comprehensive unit and integration tests**, including tests specifically for the evaluation pipeline.
