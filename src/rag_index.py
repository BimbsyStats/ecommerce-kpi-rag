"""
Shared text and vector search indexes for the ecommerce KPI RAG project.

Import from here in Notebook 03 (retrieval evaluation) and Notebook 04 (LLM evaluation)
so both notebooks test against the exact same index built in Notebook 02.

Usage:
    from rag_index import text_search, vector_search
"""
import json
import os

import numpy as np
from minsearch import Index
from sentence_transformers import SentenceTransformer

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

with open(os.path.join(_DATA_DIR, "documents.json")) as f:
    documents = json.load(f)

# --- Text search (minsearch) ---
text_index = Index(
    text_fields=["text"],
    keyword_fields=["type", "category", "country", "loyalty_tier", "month", "channel"],
)
text_index.fit(documents)


def text_search(query, num_results=5):
    return text_index.search(query, num_results=num_results)


# --- Vector search (sentence-transformers) ---
_model = SentenceTransformer("all-MiniLM-L6-v2")
_doc_texts = [d["text"] for d in documents]
_doc_embeddings = _model.encode(_doc_texts, show_progress_bar=False)


def vector_search(query, num_results=5):
    query_vec = _model.encode([query])[0]
    sims = _doc_embeddings @ query_vec / (
        np.linalg.norm(_doc_embeddings, axis=1) * np.linalg.norm(query_vec) + 1e-9
    )
    top_idx = np.argsort(sims)[::-1][:num_results]
    return [documents[i] for i in top_idx]
