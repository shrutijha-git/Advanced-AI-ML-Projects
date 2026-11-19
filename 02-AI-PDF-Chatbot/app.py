
import streamlit as st

from rag_pipeline import PDFRAGPipeline
from utils.pdf_processor import (
    extract_pdf_text,
    split_text_into_chunks,
)

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
    'Ask questions about your PDFs using Retrieval-Augmented Generation'
    '</div>',
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading AI models...")
def load_rag_pipeline():
    return PDFRAGPipeline()


with st.sidebar:
    st.header("📁 Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    st.caption(
        "Use text-based PDFs. Scanned PDFs without a text layer "
        "are not supported in this version."
    )

    process_button = st.button(
        "Process PDFs",
        type="primary",
        use_container_width=True,
    )

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_key" not in st.session_state:
    st.session_state.document_key = None

if "rag" not in st.session_state:
    st.session_state.rag = None


if process_button:
    if not uploaded_files:
        st.warning("Please upload at least one PDF.")
    else:
        with st.spinner("Extracting text and indexing documents..."):
            all_pages = []
            document_signature = []

            for uploaded_file in uploaded_files:
                pdf_bytes = uploaded_file.getvalue()
                document_signature.append(
                    (uploaded_file.name, hash(pdf_bytes))
                )

                try:
                    pages = extract_pdf_text(
                        pdf_bytes,
                        filename=uploaded_file.name,
                    )
                    all_pages.extend(pages)
                except Exception as error:
                    st.error(
                        f"Could not read {uploaded_file.name}: {error}"
                    )

            chunks = split_text_into_chunks(all_pages)

            if not chunks:
                st.error(
                    "No readable text found. Try a text-based PDF."
                )
                st.session_state.rag = None
                st.session_state.document_key = None
            else:
                try:
                    rag = load_rag_pipeline()
                    rag.index_documents(chunks)

                    st.session_state.rag = rag
                    st.session_state.document_key = tuple(
                        document_signature
                    )
                    st.session_state.messages = []

                    st.success(
                        f"Indexed {len(chunks)} text chunks "
                        f"from {len(uploaded_files)} uploaded PDFs."
                    )
                except Exception as error:
                    st.error(f"Could not build index: {error}")


if st.session_state.rag is None:
    st.info(
        "👈 Upload a PDF in the sidebar and click Process PDFs "
        "to start chatting."
    )
else:
    st.success("Documents indexed. You can ask questions!")

    if uploaded_files:
        current_signature = tuple(
            (file.name, hash(file.getvalue()))
            for file in uploaded_files
        )

        if current_signature != st.session_state.document_key:
            st.warning(
                "Your selected PDFs have changed. "
                "Click Process PDFs to update the chatbot."
            )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("📖 Source passages"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**{source['source']} — "
                            f"Page {source['page']}**"
                        )
                        st.caption(source["text"])

    question = st.chat_input(
        "Ask a question about your PDF..."
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    response = st.session_state.rag.ask(question)
                    answer = response["answer"]
                    sources = response["sources"]

                    st.markdown(answer)

                    if sources:
                        with st.expander("📖 Source passages"):
                            for source in sources:
                                st.markdown(
                                    f"**{source['source']} — "
                                    f"Page {source['page']}**"
                                )
                                st.caption(source["text"])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as error:
                    st.error(f"Could not generate answer: {error}")
