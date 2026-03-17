import re

def looks_like_variant(text: str) -> bool:
    pattern = r"^[A-Za-z0-9_-]+\s+c\.[A-Za-z0-9_>delinsdup+-]+$"
    return bool(re.match(pattern, text.strip()))