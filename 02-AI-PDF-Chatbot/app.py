
import hashlib
import threading

import streamlit as st

from rag_pipeline import PDFRAGPipeline, load_models
from utils.pdf_processor import (
    extract_pdf_text,
    split_text_into_chunks,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DocuMind AI | PDF Chatbot",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #64748b;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">📚 DocuMind AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Chat with your PDF documents using '
    'Retrieval-Augmented Generation (RAG)'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD SHARED AI MODELS
# --------------------------------------------------

@st.cache_resource(show_spinner="Loading AI models...")
def get_shared_models():
    embedding_model, tokenizer, generator = load_models()

    # Prevent concurrent generation calls from interfering.
    generation_lock = threading.Lock()

    return (
        embedding_model,
        tokenizer,
        generator,
        generation_lock,
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag" not in st.session_state:
    st.session_state.rag = None

if "document_key" not in st.session_state:
    st.session_state.document_key = None

if "generation_lock" not in st.session_state:
    st.session_state.generation_lock = None


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_document_signature(files):
    """Identify the current selection of uploaded PDFs."""
    return tuple(
        (
            file.name,
            hashlib.sha256(file.getvalue()).hexdigest(),
        )
        for file in files
    )


def clear_documents():
    """Clear this visitor's document index and chat."""
    st.session_state.messages = []
    st.session_state.rag = None
    st.session_state.document_key = None
    st.session_state.generation_lock = None


def show_sources(sources):
    """Display passages used for retrieval."""
    if not sources:
        return

    with st.expander("📖 Supporting PDF passages"):
        for source in sources:
            st.markdown(
                f"**{source['source']} — "
                f"Page {source['page']}**"
            )
            st.caption(source["text"])
            st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("📁 Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose your PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload text-based PDF documents.",
    )

    st.caption(
        "Text-based PDFs are supported. "
        "Scanned documents may require OCR."
    )

    process_button = st.button(
        "🚀 Process PDFs",
        type="primary",
        use_container_width=True,
    )

    if st.button(
        "🗑️ Clear Documents & Chat",
        use_container_width=True,
    ):
        clear_documents()
        st.rerun()

    st.divider()

    st.markdown("### About DocuMind AI")
    st.write(
        "DocuMind AI uses embeddings, FAISS vector search, "
        "and an open-source language model to answer "
        "questions about your uploaded documents."
    )

    st.caption(
        "Use non-sensitive documents. "
        "AI-generated answers may contain mistakes."
    )


# --------------------------------------------------
# PROCESS UPLOADED PDF FILES
# --------------------------------------------------

if process_button:
    if not uploaded_files:
        st.warning("Please upload at least one PDF.")

    else:
        # Invalidate previous documents before processing new ones.
        clear_documents()

        with st.spinner(
            "Reading PDFs and preparing the vector index..."
        ):
            all_pages = []
            successful_files = 0
            failed_files = []

            for uploaded_file in uploaded_files:
                try:
                    pdf_bytes = uploaded_file.getvalue()

                    pages = extract_pdf_text(
                        pdf_bytes,
                        filename=uploaded_file.name,
                    )

                    if pages:
                        all_pages.extend(pages)
                        successful_files += 1
                    else:
                        failed_files.append(
                            f"{uploaded_file.name}: "
                            "No extractable text found."
                        )

                except Exception as error:
                    failed_files.append(
                        f"{uploaded_file.name}: {error}"
                    )

            for error_message in failed_files:
                st.warning(error_message)

            if failed_files:
                st.error(
                    "One or more PDFs could not be processed. "
                    "Please correct them and try again."
                )

            else:
                chunks = split_text_into_chunks(all_pages)

                if not chunks:
                    st.error(
                        "No readable text found. "
                        "Try uploading a text-based PDF."
                    )

                else:
                    try:
                        (
                            embedding_model,
                            tokenizer,
                            generator,
                            generation_lock,
                        ) = get_shared_models()

                        # Create a NEW pipeline for this session.
                        rag = PDFRAGPipeline(
                            embedding_model=embedding_model,
                            tokenizer=tokenizer,
                            generator=generator,
                        )

                        rag.index_documents(chunks)

                        st.session_state.rag = rag
                        st.session_state.document_key = (
                            get_document_signature(uploaded_files)
                        )
                        st.session_state.generation_lock = (
                            generation_lock
                        )
                        st.session_state.messages = []

                        st.success(
                            f"Successfully processed "
                            f"{successful_files} PDF file(s) "
                            f"and indexed {len(chunks)} passages!"
                        )

                    except Exception as error:
                        clear_documents()
                        st.error(
                            f"Unable to process documents: {error}"
                        )


# --------------------------------------------------
# VERIFY THE CURRENT DOCUMENT SELECTION
# --------------------------------------------------

current_signature = (
    get_document_signature(uploaded_files)
    if uploaded_files
    else None
)

documents_ready = (
    st.session_state.rag is not None
    and current_signature == st.session_state.document_key
)

if st.session_state.rag is None:
    st.info(
        "👈 Upload your PDFs in the sidebar and "
        "click 'Process PDFs' to begin."
    )

elif not documents_ready:
    st.warning(
        "Your uploaded PDF selection has changed. "
        "Click 'Process PDFs' again before asking questions."
    )

else:
    st.success(
        "✅ Your documents are ready! "
        "Ask questions in the chat below."
    )


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

if documents_ready:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                show_sources(message["sources"])


# --------------------------------------------------
# CHAT INPUT AND RAG QUESTION ANSWERING
# --------------------------------------------------

if documents_ready:
    question = st.chat_input(
        "Ask a question about your PDF documents..."
    )

    if question and question.strip():
        question = question.strip()

        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(
                "Searching your PDFs and generating an answer..."
            ):
                try:
                    # The shared generator is protected by a lock.
                    with st.session_state.generation_lock:
                        response = st.session_state.rag.ask(
                            question
                        )

                    answer = response["answer"]
                    sources = response["sources"]

                    st.markdown(answer)
                    show_sources(sources)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as error:
                    st.error(
                        f"Could not generate an answer: {error}"
                    )
