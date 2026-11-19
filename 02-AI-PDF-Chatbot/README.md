# 📚 DocuMind AI — PDF Question-Answering Chatbot

An AI-powered PDF question-answering application using Retrieval-Augmented Generation (RAG).

Upload text-based PDF documents, ask questions in natural language, and receive generated answers supported by retrieved document passages and page references.

## Features

- Upload multiple PDF documents
- Extract PDF text using PyMuPDF
- Split text into overlapping chunks
- Generate embeddings using Sentence Transformers
- Search document chunks using FAISS
- Generate answers using FLAN-T5
- Display supporting source passages and page numbers
- Interactive Streamlit chat interface
- Automated PDF processing tests

## Technology Stack

- Python
- Streamlit
- PyMuPDF
- Sentence Transformers
- FAISS
- Hugging Face Transformers
- PyTorch
- Pytest

## RAG Workflow

1. Upload PDF documents.
2. Extract text from each PDF page.
3. Split text into overlapping chunks.
4. Convert chunks into vector embeddings.
5. Store embeddings in a FAISS index.
6. Embed the user's question.
7. Retrieve the most relevant chunks.
8. Generate an answer using the retrieved context.
9. Display the answer and supporting source passages.

## Installation

From the `Advanced-AI-ML-Projects` repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\02-AI-PDF-Chatbot\requirements.txt
```

## Run the Application

```powershell
python -m streamlit run .\02-AI-PDF-Chatbot\app.py
```

Open the local URL displayed by Streamlit, usually:

`http://localhost:8501`

## Run Tests

```powershell
python -m pytest .\02-AI-PDF-Chatbot\tests -v
```

## AI Models

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

**Answer generation model:** `google/flan-t5-small`

The models are downloaded automatically on first use.

## Limitations

- Supports text-based PDFs; OCR is not implemented.
- The lightweight generation model may produce inaccurate or incomplete answers.
- Retrieved passages are supporting evidence, not verified citations for every generated claim.
- Long contexts may be truncated by the generation model.
- The initial version is intended for local, single-user use.
- Multi-user session isolation and resource controls are required before public deployment.

## Future Improvements

- Improve source-grounded answers
- Add OCR for scanned PDFs
- Improve document chunking
- Add retrieval quality evaluation
- Support independent user sessions
- Deploy the application online
- Add screenshots and a live demo link

## Status

Initial local implementation — testing and deployment preparation.
