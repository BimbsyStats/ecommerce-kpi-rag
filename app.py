import time
import streamlit as st

from src.retrieval import build_engines
from src.rag import answer_question, PROMPT_STRICT
from src.monitoring import init_db, log_interaction

st.set_page_config(page_title="Ecommerce KPI Assistant", page_icon="📊")
init_db()

st.title("Ecommerce KPI RAG Assistant")
st.write(
    "Ask a question about revenue, categories, campaigns, or monthly "
    "trends. Answers are generated from the underlying transaction data."
)

@st.cache_resource
def get_engines():
    return build_engines()

text_engine, vector_engine = get_engines()

engine_choice = st.radio("Retrieval method", ["Text search", "Vector search"], horizontal=True)
engine = text_engine if engine_choice == "Text search" else vector_engine

question = st.text_input("Your question:", placeholder="e.g. Which category made the most revenue?")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("Ask") and question:
    with st.spinner("Retrieving and generating answer..."):
        start = time.time()
        result = answer_question(question, engine, PROMPT_STRICT)
        elapsed_ms = (time.time() - start) * 1000

        st.session_state.last_result = {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "engine": engine_choice,
            "elapsed_ms": elapsed_ms,
        }
if st.session_state.last_result:
    r = st.session_state.last_result
    st.subheader("Answer")
    st.write(r["answer"])

    st.subheader("Sources used")
    for src in r["sources"]:
        st.markdown(f"- {src['text']}")

    st.subheader("Was this helpful?")
    col1, col2 = st.columns(2)

    if col1.button("👍 Yes"):
        log_interaction(
            r["question"], r["answer"], r["engine"],
            rating=1, response_time_ms=r["elapsed_ms"]
        )
        st.success("Thanks for the feedback!")

    if col2.button("👎 No"):
        log_interaction(
            r["question"], r["answer"], r["engine"],
            rating=0, response_time_ms=r["elapsed_ms"]
        )
        st.success("Thanks for the feedback!")

