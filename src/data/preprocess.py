import unicodedata, re, html

def clean(text: str) -> str:
    # 1. Unicode normalisation
    text = unicodedata.normalize("NFKC", text)

    # 2. Strip HTML tags / entities
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)

    # 3. Remove control chars except \n\t
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # 4. Collapse redundant whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text