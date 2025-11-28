# ml/utils/preprocessing.py
import re

def clean_text(text: str) -> str:
    """
    Basic cleaning for URLs & webpage text.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9:/\.\-\_]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text