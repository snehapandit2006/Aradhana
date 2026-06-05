import re

# Set of regex patterns to check for absolute certainty statements
CERTAINTY_PATTERNS = [
    r"\b(definitely|certainly|guaranteed?|undoubtedly|100%|will surely)\b",
    r"\b(promise|assure|absolute certainty)\b",
]

# Medical, financial, and legal warning triggers (e.g. "cure", "invest", "lawsuit", "sue", "doctor", "diagnose")
RISK_TOPICS = [
    r"\b(cure|heal|treat|disease|illness|diagnose|medication|pill|doctor|health)\b",
    r"\b(invest|stock|buy|sell|bitcoin|crypto|wealth|rich|lottery|millionaire|finance|gamble|blackjack|casino|bet|assets|money)\b",
    r"\b(sue|court|lawsuit|legal|attorney|lawyer|police|judge)\b",
]

DISCLAIMER = (
    "\n\n*Disclaimer: This reading is for reflective and entertainment purposes only. "
    "Astrological insights are meant to provide perspective, not absolute guidance, and "
    "should not be taken as medical, legal, or financial advice.*"
)

def sanitize_input(text: str) -> str:
    """
    Sanitizes user input to mitigate prompt injection and remove raw HTML tags.
    """
    if not text:
        return ""
    # Strip HTML tags
    clean_text = re.sub(r'<[^>]*>', '', text)
    # Strip potential markdown code block injection wrappers
    clean_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', clean_text)  # remove control chars
    return clean_text.strip()

def has_certainty_or_risk_claims(text: str) -> bool:
    """
    Scans the response for high-certainty words combined with risk-sensitive topics.
    """
    lower_text = text.lower()
    
    # Check for direct high certainty terms
    has_certainty = any(re.search(pattern, lower_text) for pattern in CERTAINTY_PATTERNS)
    
    # Check for risk-sensitive topics
    has_risk = any(re.search(pattern, lower_text) for pattern in RISK_TOPICS)
    
    # Trigger if there is absolute certainty or if risk topics are discussed
    return has_certainty or has_risk

def apply_safety_guardrails(response_text: str) -> str:
    """
    Checks if a disclaimer needs to be appended, sanitizes absolute certainty claims, and returns the modified response text.
    """
    if not response_text:
        return ""
        
    # Sanitize absolute certainty words to enforce safety and compliance
    text_cleaned = response_text
    text_cleaned = re.sub(r"\bdefinitely\b", "likely", text_cleaned, flags=re.IGNORECASE)
    text_cleaned = re.sub(r"\bguaranteed\b", "likely", text_cleaned, flags=re.IGNORECASE)
    text_cleaned = re.sub(r"\bundoubtedly\b", "likely", text_cleaned, flags=re.IGNORECASE)
    text_cleaned = re.sub(r"\bpromises?\b", "suggest", text_cleaned, flags=re.IGNORECASE)
    text_cleaned = re.sub(r"\b100%\b", "highly likely", text_cleaned, flags=re.IGNORECASE)
        
    # Check if disclaimer is already present to prevent duplicate appending
    if "Disclaimer:" in text_cleaned:
        return text_cleaned
        
    if has_certainty_or_risk_claims(response_text):
        return text_cleaned + DISCLAIMER
        
    return text_cleaned
