"""Unit tests for Custom Data Structures and Algorithms (DSA).

Compares:
1. MinHeapTopK vs Python built-in sorted() and heapq.nlargest
2. LRUCache vs expected LRU access and eviction order
"""

import heapq
import random

import pytest

from app.core.heap_topk import MinHeapTopK, top_k_heap
from app.core.lru_cache import LRUCache


def test_min_heap_top_k_correctness():
    """Verify custom MinHeapTopK produces exact same results as Python's sorted and heapq."""
    random.seed(42)
    # Generate 200 random candidate tuples (score, item_id)
    candidates = [(round(random.uniform(0.0, 100.0), 3), f"item_{i}") for i in range(200)]
    k = 7

    # Reference ground truth using Python's built-in sorted
    ground_truth = sorted(candidates, key=lambda x: x[0], reverse=True)[:k]

    # Reference ground truth using heapq.nlargest
    heapq_truth = heapq.nlargest(k, candidates, key=lambda x: x[0])

    # Custom Min-Heap Top-K result
    custom_result = top_k_heap(candidates, k=k)

    assert len(custom_result) == k
    assert [x[0] for x in custom_result] == [x[0] for x in ground_truth]
    assert [x[0] for x in custom_result] == [x[0] for x in heapq_truth]


def test_min_heap_edge_cases():
    """Verify heap handles empty inputs, k larger than array, and k=1."""
    assert top_k_heap([], k=5) == []
    assert top_k_heap([(10.0, "a")], k=0) == []

    # K larger than items list
    items = [(5.0, "x"), (9.0, "y")]
    res = top_k_heap(items, k=10)
    assert len(res) == 2
    assert res[0] == (9.0, "y")
    assert res[1] == (5.0, "x")

    with pytest.raises(ValueError):
        MinHeapTopK(k=-1)


def test_lru_cache_operations():
    """Verify LRUCache O(1) operations, eviction order, and capacity enforcement."""
    cache = LRUCache(capacity=3)
    assert len(cache) == 0

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert len(cache) == 3
    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.get("c") == 3

    # Accessing "a" makes it most recently used; order from MRU to LRU is now: a, c, b
    assert cache.get("a") == 1

    # Adding "d" should evict "b" (least recently used)
    cache.put("d", 4)
    assert len(cache) == 3
    assert cache.get("b") is None  # Evicted!
    assert cache.get("a") == 1
    assert cache.get("c") == 3
    assert cache.get("d") == 4

    # Updating existing key
    cache.put("a", 99)
    assert cache.get("a") == 99
    assert len(cache) == 3


def test_lru_cache_clear_and_validation():
    """Verify clear() and negative capacity handling."""
    with pytest.raises(ValueError):
        LRUCache(capacity=0)

    cache = LRUCache(capacity=2)
    cache.put("x", 10)
    cache.put("y", 20)
    cache.clear()
    assert len(cache) == 0
    assert cache.get("x") is None
