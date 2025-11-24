"""LangGraph-ready tools (all decorated with @tool)."""
from langchain_core.tools import tool
from langchain_community.tools import (
    ArxivQueryRun,
    WikipediaQueryRun,
    DuckDuckGoSearchRun,
)
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.tavily_search import TavilySearchResults
import httpx, json, pathlib, typing as t

# ---------- academic / web --------------------------------------------------
@tool
def arxiv_search(query: str) -> str:
    """Search ArXiv for a paper."""
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper()).run(query)

@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia."""
    return WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()).run(query)

@tool
def duck_search(query: str) -> str:
    """DuckDuckGo instant answers."""
    return DuckDuckGoSearchRun().run(query)

# ---------- compute ---------------------------------------------------------
@tool
def python_repl(code: str) -> str:
    """Execute Python code and return stdout / stderr."""
    return PythonREPLTool().run(code)

@tool
def calculator(expr: str) -> str:
    """Safe calculator (uses Python ast)."""
    try:
        return str(eval(expr, {"__builtins__": {}}))
    except Exception as e:
        return f"Error: {e}"

# ---------- gmail (optional) -------------------------------------------------
def gmail_toolkit() -> list:
    """Returns *list* of Gmail tools ready for LangGraph."""
    return GmailToolkit().get_tools()

# ---------- weather (open-meteo) ---------------------------------------------
@tool
def weather(lat: float, lon: float) -> str:
    """Current weather at lat/lon."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = httpx.get(url, timeout=10)
    r.raise_for_status()
    return json.dumps(r.json()["current_weather"])

# ---------- io helpers -------------------------------------------------------
@tool
def scrape_url(url: str) -> str:
    """Return plain text of a web page."""
    r = httpx.get(url, timeout=15)
    r.raise_for_status()
    from bs4 import BeautifulSoup
    return BeautifulSoup(r.text, "lxml").get_text(" ", strip=True)

@tool
def file_write(path: str, content: str) -> str:
    """Write text to file (relative to cwd)."""
    pathlib.Path(path).write_text(content, encoding="utf-8")
    return f"Written to {path}"

@tool
def file_read(path: str) -> str:
    """Read text file."""
    return pathlib.Path(path).read_text(encoding="utf-8")