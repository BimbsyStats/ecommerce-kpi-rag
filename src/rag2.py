"""
Groq-based generation for the ecommerce KPI RAG assistant.

Usage:
    from src.rag_index import text_search
    from src.rag import rag_answer

    answer, sources = rag_answer("Which category generated the most revenue?", text_search)
"""
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "qwen/qwen3-32b"

PROMPT_TEMPLATE = """You are an ecommerce analytics assistant. Answer the QUESTION using only
the numbers in CONTEXT. Rules:
- Quote exact figures from the context — never estimate or round differently than the source.
- If the context does not contain the answer, say "I don't have that data" instead of guessing.
- Keep the answer to 1-2 sentences.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def build_context(results):
    return "\n".join(f"- {r['text']}" for r in results)


def rag_answer(question, search_fn, num_results=5):
    results = search_fn(question, num_results=num_results)
    context = build_context(results)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort="none",
    )
    return response.choices[0].message.content, results
