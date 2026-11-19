
import faiss
import numpy as np


class PDFVectorStore:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        if not chunks:
            raise ValueError("No text chunks available to index.")

        self.chunks = chunks

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        embeddings = np.asarray(
            embeddings, dtype=np.float32
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

    def search(self, question, top_k=3):
        if self.index is None:
            raise ValueError("Build the index before searching.")

        question_embedding = self.embedding_model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        question_embedding = np.asarray(
            question_embedding, dtype=np.float32
        )

        k = min(top_k, len(self.chunks))

        scores, indices = self.index.search(
            question_embedding, k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            results.append({
                **self.chunks[int(index)],
                "score": float(score),
            })

        return results
