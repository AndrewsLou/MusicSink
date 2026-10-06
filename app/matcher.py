import re
import unicodedata


def normalize(text: str) -> str:
    """Lowercase, strip accents/punctuation/parenthetical noise so two
    slightly-differently-formatted track names can be compared for equality."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\(.*?\)|\[.*?\]", " ", text)
    text = re.sub(r"\bfeat\.?.*", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def track_key(artist: str, title: str) -> str:
    return f"{normalize(artist)}::{normalize(title)}"
