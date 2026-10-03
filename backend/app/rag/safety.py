import re

SUSPICIOUS_PATTERNS = [
    r"ignore (all|any|the) (previous|prior|system) instructions",
    r"reveal (the )?(system|developer) prompt",
    r"show (me )?(all|the) customer database",
    r"give me (all )?private customer",
]

def sanitize_untrusted_text(text: str, max_chars: int = 12000) -> str:
    clean=text[:max_chars]
    for pattern in SUSPICIOUS_PATTERNS:
        clean=re.sub(pattern, "[redacted instruction]", clean, flags=re.I)
    return clean

def is_prompt_injection(text: str) -> bool:
    return any(re.search(p,text,re.I) for p in SUSPICIOUS_PATTERNS)
