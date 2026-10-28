"""Custom Least Recently Used (LRU) Cache Implementation from Scratch.

This module implements an O(1) time complexity LRU cache using a Doubly Linked List
combined with a Hash Map (Python dictionary).

Architecture:
1. Hash Map (dict): Maps key -> DoublyLinkedListNode for O(1) key lookups.
2. Doubly Linked List:
   - Sentinel `head` node: Represents the Most Recently Used (MRU) boundary.
   - Sentinel `tail` node: Represents the Least Recently Used (LRU) boundary.
   - Every lookup or update moves the node right after `head`.
   - Eviction removes the node right before `tail` in O(1) time.

Time Complexity:
- get(key): O(1)
- put(key, val): O(1)
Auxiliary Space Complexity: O(capacity)
"""

from typing import Any


class _Node:
    """Internal node for doubly linked list."""

    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: Any = None, val: Any = None):
        self.key = key
        self.val = val
        self.prev: _Node | None = None
        self.next: _Node | None = None


class LRUCache:
    """Thread-safe-ready, zero-dependency O(1) LRU Cache."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("LRU Cache capacity must be a positive integer greater than 0.")
        self.capacity: int = capacity
        self.cache: dict[Any, _Node] = {}

        # Initialize pseudo sentinel head and tail nodes
        self.head: _Node = _Node()
        self.tail: _Node = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def __len__(self) -> int:
        return len(self.cache)

    def _remove(self, node: _Node) -> None:
        """Unlink an existing node from its current position in the linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_front(self, node: _Node) -> None:
        """Insert a node immediately after the sentinel head (mark as most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: Any) -> Any | None:
        """Retrieve value for key and mark it as most recently used.

        Returns None if key is not found.
        """
        if key not in self.cache:
            return None

        node = self.cache[key]
        # Move node to front (MRU)
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: Any, val: Any) -> None:
        """Insert or update a key-value pair.

        If capacity is reached, evicts the least recently used item (before tail).
        """
        if key in self.cache:
            # Update existing node value and move to front
            node = self.cache[key]
            node.val = val
            self._remove(node)
            self._add_to_front(node)
            return

        # Create new node
        new_node = _Node(key=key, val=val)
        self.cache[key] = new_node
        self._add_to_front(new_node)

        # Evict least recently used if capacity exceeded
        if len(self.cache) > self.capacity:
            lru_node = self.tail.prev
            if lru_node and lru_node != self.head:
                self._remove(lru_node)
                if lru_node.key in self.cache:
                    del self.cache[lru_node.key]

    def clear(self) -> None:
        """Reset the cache to empty."""
        self.cache.clear()
        self.head.next = self.tail
        self.tail.prev = self.head
