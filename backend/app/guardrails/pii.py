"""Zero-Trust PII Masking and Sanitization Guardrail.

Protects customer privacy by detecting and redacting:
- Email addresses
- Credit and debit card numbers (with Luhn-check heuristics)
- Phone numbers (domestic US and international)
- Social Security Numbers (SSN)
"""

import re

# Compiled regex patterns for high-performance sanitization
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
)

# 13 to 19 digit card numbers with optional hyphens or spaces
CARD_PATTERN = re.compile(
    r"\b(?:\d{4}[-\s]?){3}\d{1,4}\b|\b\d{13,19}\b"
)

# US and international phone numbers
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

# Social Security Numbers (SSN)
SSN_PATTERN = re.compile(
    r"\b\d{3}-\d{2}-\d{4}\b"
)


def _is_luhn_valid(card_str: str) -> bool:
    """Validate candidate credit card string using the Luhn algorithm."""
    digits = [int(c) for c in card_str if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d
    return checksum % 10 == 0


def mask_pii(text: str) -> tuple[str, list[str]]:
    """Redact personal identifiable information from text.

    Args:
        text: Raw user message or log string.

    Returns:
        Tuple of (sanitized_text, list_of_pii_types_detected).
    """
    if not text:
        return "", []

    redacted_types = []
    sanitized = text

    # 1. Mask Email Addresses
    if EMAIL_PATTERN.search(sanitized):
        sanitized = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", sanitized)
        redacted_types.append("email")

    # 2. Mask SSNs
    if SSN_PATTERN.search(sanitized):
        sanitized = SSN_PATTERN.sub("[SSN_REDACTED]", sanitized)
        redacted_types.append("ssn")

    # 3. Mask Credit/Debit Cards
    def card_replacer(match):
        raw = match.group(0)
        digits_only = re.sub(r"\D", "", raw)
        if len(digits_only) >= 13 and (len(digits_only) == 16 or _is_luhn_valid(digits_only)):
            redacted_types.append("card")
            return "[CARD_REDACTED]"
        return raw

    sanitized = CARD_PATTERN.sub(card_replacer, sanitized)

    # 4. Mask Phone Numbers
    if PHONE_PATTERN.search(sanitized):
        sanitized = PHONE_PATTERN.sub("[PHONE_REDACTED]", sanitized)
        redacted_types.append("phone")

    # Deduplicate detected types
    unique_types = sorted(list(set(redacted_types)))
    return sanitized, unique_types


def contains_pii(text: str) -> bool:
    """Return True if any PII pattern is present in the text."""
    _, types = mask_pii(text)
    return len(types) > 0
