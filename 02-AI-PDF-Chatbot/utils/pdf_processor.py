
import fitz


def extract_pdf_text(pdf_bytes, filename="document.pdf"):
    """Extract page text from a PDF stored in memory."""
    pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "source": filename,
                    "page": page_number,
                    "text": text,
                })

    return pages


def split_text_into_chunks(pages, chunk_size=700, overlap=100):
    """Split extracted text into overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be nonnegative and smaller than chunk_size"
        )

    chunks = []
    step = chunk_size - overlap

    for page in pages:
        text = " ".join(page["text"].split())

        for start in range(0, len(text), step):
            chunk_text = text[start:start + chunk_size]

            if not chunk_text:
                continue

            chunks.append({
                "source": page["source"],
                "page": page["page"],
                "text": chunk_text,
            })

            if start + chunk_size >= len(text):
                break

    return chunks
