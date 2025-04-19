# PDF-to-Markdown Tool Evaluation

This document provides instructions for evaluating the `docling` and `marker` libraries for converting PDF technical documents to Markdown format.

## Setup

### Docling
1. Install docling:
   ```
   pip install docling
   ```
2. Basic usage:
   ```
   docling convert pdf_to_md your_document.pdf
   ```

### Marker
1. Install marker:
   ```
   pip install marker-pdf
   ```
2. Basic usage:
   ```
   marker pdf_to_md your_document.pdf
   ```

## Evaluation Process

1. **Document Selection**:
   - Choose 1-3 representative technical documents in PDF format
   - Ideally, include documents with tables, code blocks, diagrams, and complex formatting

2. **Conversion**:
   - Convert each document using both tools with default settings
   - Optionally, try different settings for each tool

3. **Evaluation Criteria**:
   - Structure preservation (headings, lists, etc.)
   - Table formatting quality
   - Code block detection
   - Handling of figures and diagrams
   - Preservation of formatting (bold, italic, etc.)
   - Overall readability of the output

4. **Recording Results**:
   - Create a simple comparison table with the evaluation criteria
   - Rate each tool on each criterion (e.g., good, fair, poor)
   - Note any specific issues or advantages

5. **Final Selection**:
   - Select the preferred tool based on the evaluation
   - Document the rationale for the selection

## Sample Evaluation Table

| Criterion | Docling | Marker | Notes |
|-----------|---------|--------|-------|
| Structure preservation | | | |
| Table formatting | | | |
| Code block detection | | | |
| Figure handling | | | |
| Text formatting | | | |
| Overall readability | | | |

## Outcomes

The results of this evaluation will inform:
1. Which tool to recommend/use for the document conversion process
2. Any known limitations to be aware of
3. Best practices for preparation of Markdown files for the RAG pipeline
