import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv() # reads your .env file so GROQ_API_KEY is available
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "qwen/qwen3.6-27b"

# Prompt style 1: strict and factual, refuses to guess
PROMPT_STRICT = """You are a precise data analyst assistant. Answer the
question using ONLY the context below. If the answer is not in the
context, say "I don't have that information."

CONTEXT:
{context}

QUESTION: {question}

ANSWER (be concise and factual, cite numbers exactly as given):"""

# Prompt style 2: friendlier, conversational tone
PROMPT_CONVERSATIONAL = """You are a friendly business intelligence
assistant helping an ecommerce team understand their KPIs. Use the
context below to answer naturally, as if explaining to a colleague.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

def build_context(retrieved_docs):
    # Joins all retrieved sentences into one block of text for the prompt
    return "\n".join(d["text"] for d in retrieved_docs)

def answer_question(question, engine, prompt_template=PROMPT_STRICT, top_k=5):
     # Step 1: find the most relevant sentences (using retrieval.py)
    retrieved = engine.search(question, top_k=top_k)
    # Step 2: build the context block from those sentences
    context = build_context(retrieved)
    # Step 3: fill in the prompt template with context + question
    prompt = prompt_template.format(context=context, question=question)
    # Step 4: send it to the Groq LLM and get the answer back
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort="none",
    )
    return {"answer": response.choices[0].message.content, "sources": retrieved}

if __name__ == "__main__":
    from src.retrieval import build_engines
    text_engine, vector_engine = build_engines()
    question = "Which product category generated the most revenue?"
    print("--- Strict prompt ---")
    result = answer_question(question, text_engine, PROMPT_STRICT)
    print(result["answer"])
    print("\n--- Conversational prompt ---")
    result2 = answer_question(question, text_engine, PROMPT_CONVERSATIONAL)
    print(result2["answer"])