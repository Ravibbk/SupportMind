"""Custom Min-Heap Top-K Implementation from Scratch.

This module provides an efficient O(N log K) algorithm to retrieve the top-K highest
scoring elements from a collection of N candidates without sorting the entire array (O(N log N)).

Algorithm Details:
1. Maintain a min-heap of maximum size K.
2. The root of the min-heap always contains the smallest score among the current top-K candidates.
3. For each incoming candidate (score, item):
   - If heap size < K: insert candidate and percolate up.
   - Else if score > root score: replace root and percolate down.
   - Else: discard candidate (since it cannot be in the top K).
4. Extract all elements from the heap and sort them descending (taking O(K log K)).
Total Time Complexity: O(N log K)
Auxiliary Space Complexity: O(K)
"""

from typing import Any


class MinHeapTopK:
    """A min-heap designed specifically for tracking top-K maximum elements."""

    def __init__(self, k: int):
        if k <= 0:
            raise ValueError("K must be a positive integer greater than 0.")
        self.k = k
        # Internal array storing tuples of (score, item)
        self.heap: list[tuple[float, Any]] = []

    def __len__(self) -> int:
        return len(self.heap)

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _sift_up(self, idx: int) -> None:
        """Percolate an element up until the heap property (parent <= child) is restored."""
        current = idx
        while current > 0:
            p = self._parent(current)
            if self.heap[current][0] < self.heap[p][0]:
                self._swap(current, p)
                current = p
            else:
                break

    def _sift_down(self, idx: int) -> None:
        """Percolate an element down until the heap property (parent <= child) is restored."""
        size = len(self.heap)
        current = idx
        while True:
            smallest = current
            left = self._left_child(current)
            right = self._right_child(current)

            if left < size and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < size and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right

            if smallest != current:
                self._swap(current, smallest)
                current = smallest
            else:
                break

    def push(self, score: float, item: Any) -> None:
        """Insert a candidate (score, item) into the top-K tracker.

        If the heap already has K elements, only keep the element if score > root.
        """
        element = (score, item)
        if len(self.heap) < self.k:
            # Heap is not full yet: append and sift up
            self.heap.append(element)
            self._sift_up(len(self.heap) - 1)
        elif score > self.heap[0][0]:
            # Element is greater than the current minimum in the top-K set: replace root and sift down
            self.heap[0] = element
            self._sift_down(0)

    def get_top_k(self) -> list[tuple[float, Any]]:
        """Return the top-K elements sorted in descending order of score."""
        # Sort internal heap descending by score
        return sorted(self.heap, key=lambda x: x[0], reverse=True)


def top_k_heap(candidates: list[tuple[float, Any]], k: int) -> list[tuple[float, Any]]:
    """Helper function to extract top-K items from an iterable of (score, item) pairs.

    Args:
        candidates: List of (score, item) tuples.
        k: Maximum number of elements to retrieve.

    Returns:
        List of (score, item) tuples sorted in descending order of score.
    """
    if k <= 0 or not candidates:
        return []

    heap = MinHeapTopK(k=k)
    for score, item in candidates:
        heap.push(score, item)

    return heap.get_top_k()
