import json
from pathlib import Path

import minsearch
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_documents():
    """Reads the sentences that build_documents.py created."""
    with open(DATA_DIR / "documents.json") as f:
        return json.load(f)


class TextSearchEngine:
    """
    Approach 1: Keyword/TF-IDF style search using minsearch.

    Matches based on shared WORDS — like Ctrl+F, but smarter.
    """

    def __init__(self, documents):
        self.documents = documents
        self.index = minsearch.Index(
            text_fields=["text", "type"],
            keyword_fields=[]
        )

        # Builds the searchable index once
        self.index.fit(documents)

    def search(self, query, top_k=5):
        return self.index.search(query, num_results=top_k)


class VectorSearchEngine:
    """
    Approach 2: Embedding-based semantic search.

    Matches based on MEANING, not exact words.
    """

    def __init__(self, documents, model_name="all-MiniLM-L6-v2"):
        self.documents = documents
        self.model = SentenceTransformer(model_name)

        texts = [d["text"] for d in documents]

        # Turn every sentence into an embedding
        self.embeddings = self.model.encode(
            texts,
            show_progress_bar=False
        )

    def search(self, query, top_k=5):
        # Encode the user's question
        query_vec = self.model.encode([query])[0]

        # Compute cosine similarity
        sims = np.dot(self.embeddings, query_vec) / (
            np.linalg.norm(self.embeddings, axis=1)
            * np.linalg.norm(query_vec)
            + 1e-10
        )

        # Get the top matching documents
        top_idx = np.argsort(sims)[::-1][:top_k]

        return [self.documents[i] for i in top_idx]


def build_engines():
    documents = load_documents()

    text_engine = TextSearchEngine(documents)
    vector_engine = VectorSearchEngine(documents)

    return text_engine, vector_engine


if __name__ == "__main__":
    text_engine, vector_engine = build_engines()

    query = "Which category made the most revenue?"

    print("--- Text search results ---")
    for r in text_engine.search(query, top_k=3):
        print(r["text"])

    print("\n--- Vector search results ---")
    for r in vector_engine.search(query, top_k=3):
        print(r["text"])
