"""Unit tests for the Evaluation Lab metrics calculation engine."""

from app.rag.chunker import Chunk
from eval.run_eval import evaluate_answer_correctness, evaluate_retrieval, load_eval_set


def test_eval_set_loading_and_schema():
    """Verify eval_set.json contains 60 properly structured queries."""
    items = load_eval_set()
    assert len(items) == 60
    for item in items:
        assert "id" in item
        assert "question" in item
        assert "expected_document" in item
        assert "is_unanswerable" in item
        assert "is_adversarial" in item


def test_evaluate_retrieval_hit_and_mrr():
    """Verify Hit-Rate@K and MRR computation."""
    c1 = Chunk("c1", "Text 1", "returns_refunds.md", "Sec1", 0)
    c2 = Chunk("c2", "Text 2", "shipping_delivery.md", "Sec2", 1)
    c3 = Chunk("c3", "Text 3", "payments_billing.md", "Sec3", 2)

    # Expected doc at rank 1
    r1 = evaluate_retrieval([c1, c2, c3], expected_doc="returns_refunds.md", k=4)
    assert r1["hit"] == 1.0
    assert r1["mrr"] == 1.0

    # Expected doc at rank 2
    r2 = evaluate_retrieval([c1, c2, c3], expected_doc="shipping_delivery.md", k=4)
    assert r2["hit"] == 1.0
    assert r2["mrr"] == 0.5

    # Expected doc missing
    r3 = evaluate_retrieval([c1, c2, c3], expected_doc="warranty_repairs.md", k=4)
    assert r3["hit"] == 0.0
    assert r3["mrr"] == 0.0


def test_evaluate_answer_correctness():
    """Verify correctness scoring via keyword coverage and refusal handling."""
    # Answer contains all expected keywords
    ans1 = "The standard return window is 30 days from confirmed delivery in original condition."
    score1 = evaluate_answer_correctness(ans1, ["30-day", "delivery", "original condition"], False, False)
    assert score1 >= 0.66

    # Unanswerable query refused correctly
    score2 = evaluate_answer_correctness("I cannot answer.", ["some_kw"], is_unanswerable=True, is_refused=True)
    assert score2 == 1.0

    # Unanswerable query that hallucinated instead of refusing
    score3 = evaluate_answer_correctness("Yes we do sell airplanes.", ["some_kw"], is_unanswerable=True, is_refused=False)
    assert score3 == 0.0
