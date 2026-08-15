def hit_rate(results_list, ground_truth_ids):
    hits = 0
    for results, correct_id in zip(results_list, ground_truth_ids):
        if correct_id in results:
            hits += 1

    if len(ground_truth_ids) == 0:
        return 0.0

    return hits / len(ground_truth_ids)

def mrr(results_list, ground_truth_ids):
    total = 0.0
    for results, correct_id in zip(results_list, ground_truth_ids):
        if correct_id in results:
            rank = results.index(correct_id) + 1
            total += 1 / rank

    if len(ground_truth_ids) == 0:
         return 0.0

    return total / len(ground_truth_ids)

def evaluate_engine(engine, test_questions, top_k=5):
    results_list = []
    ground_truth_ids = []

    for item in test_questions:
        results = engine.search(item["question"], top_k=top_k)
        result_ids = [r["id"] for r in results]
        results_list.append(result_ids)
        ground_truth_ids.append(item["doc_id"])

    return {
        "hit_rate": hit_rate(results_list, ground_truth_ids),
        "mrr": mrr(results_list, ground_truth_ids),
    }

if __name__ == "__main__":
    from src.retrieval import build_engines
    test_questions = [
        {"question": "What is the overall revenue summary?", "doc_id": "summary-0"},
        {"question": "How much revenue did category 0 generate?", "doc_id": "category-0"},
    ]
    text_engine, vector_engine = build_engines()
print("Text search:", evaluate_engine(text_engine, test_questions))
print("Vector search:", evaluate_engine(vector_engine, test_questions))