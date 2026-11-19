
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

from utils.vector_store import PDFVectorStore


class PDFRAGPipeline:
    def __init__(self):
        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
        )

        print("Loading answer generation model...")

        model_name = "google/flan-t5-small"

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        self.generator = AutoModelForSeq2SeqLM.from_pretrained(
            model_name
        )

        self.generator.eval()

        self.vector_store = PDFVectorStore(
            self.embedding_model
        )

    def index_documents(self, chunks):
        self.vector_store.build_index(chunks)

    def ask(self, question):
        results = self.vector_store.search(
            question, top_k=3
        )

        if not results:
            return {
                "answer": "No relevant information was found.",
                "sources": [],
            }

        context = "\n\n".join(
            f"[{item['source']}, page {item['page']}] "
            f"{item['text']}"
            for item in results
        )

        prompt = (
            "Answer the question using only the context below. "
            "If the context does not contain the answer, "
            "say 'I could not find the answer in the PDF.'\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )

        with torch.no_grad():
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
