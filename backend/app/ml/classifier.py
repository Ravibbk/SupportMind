"""Production Ticket Classification and Urgency Inference Module.

Exposes:
- TicketClassificationResult (Pydantic schema)
- predict(text: str) -> TicketClassificationResult
"""

import re
from pathlib import Path

import joblib
from pydantic import BaseModel, Field

# Model artifact paths
MODEL_PATH = Path(__file__).resolve().parent / "ticket_classifier.joblib"

# Global cached model instance
_MODEL = None


class TicketClassificationResult(BaseModel):
    """Structured response schema for ticket classification."""

    category: str = Field(..., description="Predicted inquiry category: billing, delivery, refund, account, product, other")
    urgency: str = Field(..., description="Urgency level: low, medium, or high")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the predicted category")
    probabilities: dict[str, float] = Field(default_factory=dict, description="Class probability distribution")


# Lexicons for urgency heuristic scoring
HIGH_URGENCY_KEYWORDS = {
    "unauthorized", "stolen", "lawyer", "attorney", "chargeback", "police",
    "fraud", "fraudulent", "urgent", "asap", "immediately", "ruined", "emergency",
    "furious", "twice", "double charged", "locked out", "scam"
}

LOW_URGENCY_KEYWORDS = {
    "retail store", "hiring", "wholesale", "dimensions", "manual", "specifications",
    "cool", "black friday", "sponsorship", "just wondering", "curious"
}


def _load_model():
    """Load and cache the trained scikit-learn pipeline."""
    global _MODEL
    if _MODEL is None and MODEL_PATH.exists():
        try:
            _MODEL = joblib.load(MODEL_PATH)
        except Exception:
            _MODEL = None
    return _MODEL


def predict_urgency(text: str, category: str, confidence: float) -> str:
    """Determine urgency level combining keyword heuristics and category signals."""
    clean_text = text.lower()

    # Rule 1: High urgency triggers
    for kw in HIGH_URGENCY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", clean_text):
            return "high"

    # Rule 2: Low urgency triggers
    for kw in LOW_URGENCY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", clean_text):
            return "low"

    if category == "other":
        return "low"

    # Rule 3: Default baseline is medium
    return "medium"


def predict(text: str | None) -> TicketClassificationResult:
    """Predict category, urgency, and confidence for a given customer inquiry.

    Args:
        text: Raw customer inquiry text.

    Returns:
        TicketClassificationResult with category, urgency, and confidence score.
    """
    # Edge case: Empty, None, or whitespace-only inputs
    if not text or not text.strip():
        return TicketClassificationResult(
            category="other",
            urgency="low",
            confidence=0.0,
            probabilities={"other": 1.0}
        )

    clean_text = text.strip()
    model = _load_model()

    # Fallback if model binary is not loaded
    if model is None:
        return _rule_based_fallback(clean_text)

    try:
        # Predict class probabilities
        probs = model.predict_proba([clean_text])[0]
        classes = model.classes_
        prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, probs, strict=False)}

        # Find best class and confidence
        best_idx = probs.argmax()
        category = str(classes[best_idx])
        confidence = round(float(probs[best_idx]), 4)

        # Determine urgency
        urgency = predict_urgency(clean_text, category, confidence)

        return TicketClassificationResult(
            category=category,
            urgency=urgency,
            confidence=confidence,
            probabilities=prob_dict
        )
    except Exception:
        return _rule_based_fallback(clean_text)


def _rule_based_fallback(text: str) -> TicketClassificationResult:
    """Robust zero-dependency fallback classifier."""
    lowered = text.lower()
    if any(k in lowered for k in ["charge", "card", "bill", "invoice", "receipt", "fee", "tax"]):
        cat = "billing"
    elif any(k in lowered for k in ["track", "ship", "deliver", "delay", "carrier", "fedex", "ups"]):
        cat = "delivery"
    elif any(k in lowered for k in ["return", "refund", "exchange", "money back"]):
        cat = "refund"
    elif any(k in lowered for k in ["password", "login", "account", "lock", "gdpr", "email"]):
        cat = "account"
    elif any(k in lowered for k in ["warranty", "repair", "spec", "headphone", "device", "manual"]):
        cat = "product"
    else:
        cat = "other"

    urgency = predict_urgency(text, cat, 0.75)
    return TicketClassificationResult(
        category=cat,
        urgency=urgency,
        confidence=0.75,
        probabilities={cat: 0.75}
    )
