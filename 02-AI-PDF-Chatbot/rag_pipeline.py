
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from utils.vector_store import PDFVectorStore


class PDFRAGPipeline:
    def __init__(self, embedding_model, tokenizer, generator):
        # Shared, read-only AI models
        self.embedding_model = embedding_model
        self.tokenizer = tokenizer
        self.generator = generator

        # A separate vector store for each pipeline instance
        self.vector_store = PDFVectorStore(embedding_model)

    def index_documents(self, chunks):
        self.vector_store.build_index(chunks)

    def ask(self, question):
        if not question or not question.strip():
            return {
                "answer": "Please enter a question.",
                "sources": [],
            }

        results = self.vector_store.search(
            question.strip(),
            top_k=3,
        )

        if not results:
            return {
                "answer": "No relevant information was found.",
                "sources": [],
            }

        # Keep the context short enough for FLAN-T5-small.
        context = "\n\n".join(
            f"[{item['source']}, page {item['page']}] "
            f"{item['text'][:500]}"
            for item in results
        )

        prompt = (
            "Answer using only the context. "
            "If the answer is not in the context, say "
            "'I could not find the answer in the PDF.'\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question.strip()}\n"
            "Answer:"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )

        with torch.inference_mode():
            outputs = self.generator.generate(
                **inputs,
                max_new_tokens=120,
                num_beams=3,
                do_sample=False,
            )

        answer = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        ).strip()

        return {
            "answer": answer or "No answer generated.",
            "sources": results,
        }


def load_models():
    """Load reusable AI models without storing document data."""
    embedding_model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu",
    )

    model_name = "google/flan-t5-small"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    generator = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    generator.to("cpu")
    generator.eval()

    return embedding_model, tokenizer, generator
