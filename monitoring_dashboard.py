import streamlit as st
import pandas as pd
from src.monitoring import get_all_feedback

st.set_page_config(page_title="RAG Monitoring Dashboard", page_icon="\U0001F4C8")
st.title("Monitoring Dashboard")

df = get_all_feedback()

if df.empty:
    st.info("No interactions logged yet. Use the app first.")
else:
    st.metric("Total questions asked", len(df))
    st.metric(
        "Average rating",
        round(df["rating"].dropna().mean(), 2) if df["rating"].notna().any() else "N/A",
    )
    st.metric("Average response time (ms)", round(df["response_time_ms"].mean(), 1))

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    st.subheader("Questions per day")
    st.bar_chart(df.groupby("date").size())

    st.subheader("Retrieval engine usage")
    st.bar_chart(df["engine"].value_counts())

    st.subheader("Rating distribution")
    st.bar_chart(df["rating"].value_counts().sort_index())

    st.subheader("Response time trend")
    st.line_chart(df.set_index("timestamp")["response_time_ms"])

    st.subheader("Recent questions")
    st.dataframe(df[["timestamp", "question", "engine", "rating"]].tail(20))
