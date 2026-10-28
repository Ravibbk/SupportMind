"""Abstract Base Class for LLM Providers.

Decouples the SupportMind application from specific model APIs (Gemini, Claude, OpenAI).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Standardized response from an LLM call."""

    content: str
    model_name: str
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract interface for large language model providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """Generate raw text response from the model."""
        pass

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.1
    ) -> dict[str, Any]:
        """Generate validated JSON matching the expected structured format."""
        pass
