# Ecommerce KPI RAG

A Retrieval-Augmented Generation system for answering natural-language questions about
ecommerce KPIs — revenue, orders, refund rates, and trends by category, country, loyalty tier,
month, and marketing channel. Built for the [LLM Zoomcamp 2026](https://github.com/DataTalksClub/llm-zoomcamp)
capstone project.

## Example questions it can answer

- "Which product category generated the most revenue?"
- "What's the average order value in Electronics?"
- "How much revenue came from the Email marketing channel?"
- "What was total revenue in the US?"
- "What's the refund rate overall?"

## Dataset

[Marketing & E-Commerce Analytics Dataset](https://www.kaggle.com/datasets/geethasagarbonthu/marketing-and-e-commerce-analytics-dataset)
(Kaggle) — five tables covering 2021-2023:

| File | Rows | Description |
|---|---|---|
| `customers.csv` | 100,000 | customer_id, signup_date, country, age, gender, loyalty_tier, acquisition_channel |
| `products.csv` | 2,000 | product_id, category, brand, base_price, launch_date, is_premium |
| `transactions.csv` | 103,127 | transaction_id, timestamp, customer_id, product_id, quantity, discount_applied, gross_revenue, campaign_id, refund_flag |
| `campaigns.csv` | 50 | campaign_id, channel, objective, start_date, end_date, target_segment, expected_uplift |
| `events.csv` | 2,000,000 | *not used in this pipeline* — see note below |

`events.csv` is excluded because it isn't needed for KPI reporting and, at ~170MB, exceeds
GitHub's 100MB file size limit. It's downloaded automatically at container startup via the
Kaggle API if a future analysis needs it (`scripts/download_data.sh`) — it never needs to be
committed to the repo.

**Known data quality issue:** 10,449 transactions (~10.1%) are missing `product_id` and
`gross_revenue` in the raw source data. These rows are excluded from revenue calculations
(see Notebook 01) rather than imputed, since there's no reliable way to recover the missing
values.

## Architecture

```
CSV files (customers, products, transactions, campaigns)
        |
   01_explore_data.ipynb        -> merged_transactions.csv
        |
   02_build_rag_pipeline.ipynb  -> documents.json (59 KPI summary documents)
        |                          + text index (minsearch) + vector index (sentence-transformers)
        |
   03_retrieval_evaluation.ipynb -> Hit Rate / MRR comparison, text vs. vector search
   04_llm_evaluation.ipynb       -> faithfulness / relevance comparison, two prompt strategies
        |
   Streamlit app (app.py)  <-- retrieval + Groq generation, using the winning configuration
```

**Retrieval flow:** question -> retrieve top-5 KPI documents (text or vector search) -> build
prompt with retrieved context -> Groq (`openai/gpt-oss-120b`) -> answer.

Rather than indexing raw transactions, the pipeline pre-aggregates the data into 59 short KPI
summary documents (one per category, country, loyalty tier, month, and campaign channel, plus
one overall summary). This keeps retrieval focused on the kind of question users actually ask
("how much revenue did X generate") instead of matching against individual order rows.

## Project structure

```
|   .env.example
|   .gitignore
|   app.py                # Streamlit interface
|   docker-compose.yml
|   Dockerfile
|   feedback.db
|   monitoring_dashboard.py
|   README.md
|   requirements.txt
|
+---data
|       campaigns.csv
|       category_revenue.png
|       customers.csv
|       documents.json   # output of Notebook 02
|       eval_questions.json   # output of Notebook 03
|       events.csv
|       llm_eval_results.json
|       merged_transactions.csv  # output of Notebook 01
|       monthly_revenue.png
|       products.csv
|       transactions.csv
|       
+---docs
|       screenshots
|       
+---notebooks
|       01_explore_data.ipynb
|       02_build_rag_pipeline.ipynb
|       03_retrieval_evaluation.ipynb
|       04_llm_evaluation.ipynb
|       
+---src
|   |   build_documents.py
|   |   evaluation.py
|   |   ingest.py  # builds documents.json from the CSVs   
|   |   load_data.py
|   |   monitoring.py
|   |   rag.py  # Groq generation
|   |   rag_index.py  # shared text_search / vector_search functions
|   |   retrieval.py
|           
\---tests
    |   test_retrieval.py
    |   
 \---scripts
     |    download_data.sh    # fetches events.csv from Kaggle if needed (not committed)

```

## Setup

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Add your Groq API key to a `.env` file (never commit this):
   ```
   GROQ_API_KEY=your_key_here
   ```
3. Run the notebooks in order (01 -> 04) to rebuild `documents.json` and the evaluation
   results, or use the pre-built `data/documents.json` included in the repo.
4. Launch the app:
   ```
   streamlit run app.py
   ```

### Running with Docker

```
docker compose up --build
```

If `events.csv` is needed for a future analysis, add your Kaggle credentials
(`KAGGLE_USERNAME`, `KAGGLE_KEY`) as environment variables — `scripts/download_data.sh` fetches
it automatically before the app starts.

## Evaluation summary

Retrieval and LLM evaluation are run in Notebooks 03 and 04. Fill in these tables after
running them locally (they require `minsearch`, `sentence-transformers`, and a Groq API key,
so results aren't pre-computed in this repo):

**Retrieval — Hit Rate / MRR @ k=6** (72 evaluation questions, one ground-truth document per question)

| Approach | Hit Rate@6 | MRR@6 |
|---|------------|-------|
| Text search (minsearch) | 1.000      | 0.859 |
| Vector search (sentence-transformers) | 0.764      | 0.632 |

**Generation — LLM-as-judge, 1-5 scale** (15-question sample)

| Prompt | Avg. Faithfulness | Avg. Relevance |
|---|-------------------|----------------|
| Minimal | 5.0               | 5.0            |
| Structured | 5.0               | 5.0            |
## Generation summary
Both the minimal and structured prompts scored a perfect 5.0/5.0 on faithfulness and relevance across the 15-question sample. This ceiling effect suggests the current evaluation questions — direct, single-fact KPI lookups with unambiguous context — don't sufficiently stress-test prompt differences. A more discriminating test set would include multi-step or comparative questions (e.g. "compare Electronics and Home revenue") where the structured prompt's explicit citation and "admit uncertainty" instructions would more likely diverge from the minimal prompt's behavior.


## Dataset summary

From Notebook 01, computed on the full transaction table:

- **103,127 transactions**, **100,000 customers**, **2,000 products**, **6 categories**
  (Electronics, Home, Fashion, Sports, Beauty, Grocery)
- **Total revenue: $8,373,966.36** (Jan 2021 - Dec 2023), average order value **$90.36**
- **Refund rate: 2.94%**
- Electronics is the top-revenue category (~$3.45M); Grocery is the lowest (~$292K)
- US is the top-revenue country (~$2.95M); Australia is the lowest (~$591K)

## AI-assisted analysis

Built with assistance from Claude (Anthropic) for notebook scaffolding, KPI document design,
and this README. All figures were computed directly from the source data and verified before
inclusion — see Notebook 01 for the underlying calculations.
