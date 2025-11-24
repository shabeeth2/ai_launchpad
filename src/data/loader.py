"""
Load common file types + web pages.
Return: list[dict]  ->  [{ "text": "...", "meta": {...} }, ...]
"""
from pathlib import Path
import json, requests, bs4
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
)

SUPPORTED = {".pdf", ".txt", ".md", ".json"}

def load(path: str | Path) -> list[dict]:
    path = Path(path)
    suffix = path.suffix.lower()

    # --- local files 
    if path.exists():
        if suffix == ".pdf":
            docs = PyPDFLoader(str(path)).load()
        elif suffix == ".txt":
            docs = TextLoader(str(path), encoding="utf-8").load()
        elif suffix == ".md":
            docs = UnstructuredMarkdownLoader(str(path)).load()
        elif suffix == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            docs = [{"page_content": json.dumps(raw), "metadata": {}}]
        else:
            raise ValueError(f"Unsupported local file type: {suffix}")
        return [{"text": d.page_content, "meta": d.metadata} for d in docs]

    # if its a url
    if str(path).startswith("http"):
        r = requests.get(str(path), timeout=15)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, "lxml")
        return [{"text": soup.get_text(" ", strip=True),
                 "meta": {"source": str(path)}}]

    raise FileNotFoundError(f"Path/URL not found: {path}")