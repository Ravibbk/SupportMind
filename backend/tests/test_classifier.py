"""Unit tests for the Ticket Classifier module."""

import pytest

from app.ml.classifier import TicketClassificationResult, predict


def test_classifier_predict_billing():
    """Verify billing inquiry is classified accurately."""
    res = predict("Why was my credit card charged twice for order ORD-10492?")
    assert isinstance(res, TicketClassificationResult)
    assert res.category == "billing"
    assert res.confidence > 0.5
    assert "billing" in res.probabilities


def test_classifier_predict_delivery():
    """Verify delivery inquiry is classified accurately."""
    res = predict("My package was supposed to arrive yesterday, tracking has not updated!")
    assert res.category == "delivery"
    assert res.confidence > 0.5


def test_classifier_predict_refund():
    """Verify return and refund request is classified accurately."""
    res = predict("I want to return the headphones and get a full refund label.")
    assert res.category == "refund"
    assert res.confidence > 0.5


def test_classifier_predict_account():
    """Verify account and security issue is classified accurately."""
    res = predict("My account is locked and I cannot reset my password.")
    assert res.category == "account"
    assert res.confidence > 0.5


def test_classifier_predict_product():
    """Verify product hardware and warranty query is classified accurately."""
    res = predict("Does the mechanical keyboard have a 1-year manufacturer warranty?")
    assert res.category == "product"
    assert res.confidence > 0.5


def test_classifier_predict_other():
    """Verify general corporate inquiry is classified as other."""
    res = predict("Are you currently hiring customer service representatives in Chicago?")
    assert res.category == "other"
    assert res.urgency == "low"


def test_urgency_detection_high():
    """Verify high urgency flag is activated on critical keywords."""
    res = predict("URGENT: unauthorized charge on my account, cancel immediately or I call my lawyer!")
    assert res.urgency == "high"


def test_urgency_detection_low():
    """Verify low urgency flag is activated for informational queries."""
    res = predict("What are the dimensions and specifications of the office chair?")
    assert res.urgency == "low"


@pytest.mark.parametrize("empty_input", ["", "   ", "\n\t", None])
def test_classifier_empty_input_graceful_handling(empty_input):
    """Verify classifier safely handles empty or None strings without raising exceptions."""
    res = predict(empty_input)
    assert res.category == "other"
    assert res.confidence == 0.0
    assert res.urgency == "low"


def test_classifier_noisy_and_typo_input():
    """Verify classifier handles informal slang, emojis, and typos."""
    res = predict("teh pakage is delayed plz help asap!!! 😡📦")
    assert res.category == "delivery"
    assert res.urgency == "high"
