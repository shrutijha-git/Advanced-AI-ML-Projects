
import sys
from pathlib import Path

import fitz
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from utils.pdf_processor import (
    extract_pdf_text,
    split_text_into_chunks,
)


def create_sample_pdf():
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Machine learning helps computers learn from data."
    )
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_extract_pdf_text():
    pages = extract_pdf_text(
        create_sample_pdf(),
        filename="sample.pdf",
    )

    assert len(pages) == 1
    assert pages[0]["source"] == "sample.pdf"
    assert pages[0]["page"] == 1
    assert "Machine learning" in pages[0]["text"]


def test_split_text_into_chunks():
    pages = [{
        "source": "test.pdf",
        "page": 2,
        "text": "Artificial intelligence " * 30,
    }]

    chunks = split_text_into_chunks(
        pages,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= 100 for chunk in chunks)
    assert all(chunk["page"] == 2 for chunk in chunks)


def test_empty_pages():
    assert split_text_into_chunks([]) == []


def test_invalid_overlap():
    with pytest.raises(ValueError):
        split_text_into_chunks(
            [{"source": "a.pdf", "page": 1, "text": "hello"}],
            chunk_size=100,
            overlap=100,
        )


def test_invalid_pdf():
    with pytest.raises(Exception):
        extract_pdf_text(b"not a real PDF")
