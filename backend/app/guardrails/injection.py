"""Adversarial Prompt-Injection and Jailbreak Defense Guardrail.

Protects against:
1. System prompt overrides ("ignore previous instructions", "disregard rules")
2. Persona hijacking and jailbreaks ("DAN mode", "developer mode unlocked")
3. Delimiter injection and token forgery ("<|im_start|>", "--- END PROMPT ---")
4. Prompt leak and exfiltration ("print your system prompt", "reveal developer instructions")
5. Malicious SQL / code injection payloads in chat queries
"""

import re
from dataclasses import dataclass

# High-risk adversarial heuristics
INJECTION_PATTERNS = [
    # 1. Instruction overrides
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.I), "Instruction override attempt"),
    (re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|guidelines)", re.I), "Instruction override attempt"),
    (re.compile(r"forget\s+(everything|all\s+prior\s+instructions|system\s+prompt)", re.I), "Memory wipe override attempt"),
    (re.compile(r"override\s+(system|developer|safety)\s+(prompt|settings|instructions)", re.I), "System override attempt"),

    # 2. Jailbreaks and Persona hijacking
    (re.compile(r"\b(dan\s+mode|jailbreak|unrestricted\s+ai|evil\s+bot)\b", re.I), "Persona jailbreak attempt"),
    (re.compile(r"you\s+are\s+now\s+(in\s+developer\s+mode|unfiltered|free\s+of\s+rules)", re.I), "Developer mode jailbreak"),
    (re.compile(r"pretend\s+you\s+(are\s+not\s+an\s+ai|have\s+no\s+ethics|are\s+unconstrained)", re.I), "Constraint relaxation attempt"),

    # 3. Delimiter / Token forgery
    (re.compile(r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>", re.I), "Special token injection"),
    (re.compile(r"\[/?(system|instruction|prompt)\]", re.I), "System tag forgery"),
    (re.compile(r"---+\s*(?:end|begin)[\s\w]+---+", re.I), "Delimiter breakout attempt"),

    # 4. Prompt exfiltration
    (re.compile(r"(repeat|print|reveal|show|output)\s+(your\s+)?(system\s+prompt|initial\s+instructions|secret\s+instructions)", re.I), "System prompt exfiltration"),
    (re.compile(r"what\s+(are|were)\s+your\s+(exact\s+)?(initial\s+instructions|system\s+rules)", re.I), "System prompt exfiltration"),

    # 5. Malicious code / SQL injection patterns
    (re.compile(r";\s*(drop\s+table|delete\s+from|update\s+orders|insert\s+into)", re.I), "SQL injection attack"),
    (re.compile(r"(union\s+select|1=1\s*--|admin'\s*--|'\s*or\s+'1'='1)", re.I), "SQL injection signature"),
    (re.compile(r"(os\.system|subprocess\.Popen|__import__|eval\(|exec\()", re.I), "Code execution injection")
]


@dataclass
class InjectionCheckResult:
    """Security verification result for an incoming customer message."""

    is_safe: bool
    risk_score: float  # 0.0 (clean) to 1.0 (dangerous)
    reason: str | None = None
    matched_patterns: list[str] | None = None


def check_prompt_injection(text: str) -> InjectionCheckResult:
    """Scan text for adversarial prompt-injection attempts.

    Args:
        text: Inbound customer inquiry.

    Returns:
        InjectionCheckResult with safety verdict and risk score.
    """
    if not text or not text.strip():
        return InjectionCheckResult(is_safe=True, risk_score=0.0)

    clean_text = text.strip()
    matches = []

    for pattern, reason in INJECTION_PATTERNS:
        if pattern.search(clean_text):
            matches.append(reason)

    if matches:
        return InjectionCheckResult(
            is_safe=False,
            risk_score=round(min(1.0, 0.4 + 0.3 * len(matches)), 2),
            reason=matches[0],
            matched_patterns=matches
        )

    return InjectionCheckResult(is_safe=True, risk_score=0.0)


def get_safe_refusal_message(reason: str | None = None) -> str:
    """Standardized polite refusal response when an adversarial attack is blocked."""
    return (
        "I'm sorry, but I cannot fulfill this request as it violates NovaCart safety guidelines. "
        "I am SupportMind, an AI assistant dedicated exclusively to helping you with your NovaCart orders, "
        "shipping, returns, and store policies."
    )
