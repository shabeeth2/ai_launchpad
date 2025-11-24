from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from loguru import logger

from src.llm.config import settings

def get_llm(
    temperature: float = 0.0,
    model: Optional[str] = None,
    streaming: bool = True,
    json_mode: bool = False
) -> ChatOpenAI:
    """
    Creates a standard LLM client.
    """
    
    model_to_use = model or settings.MODEL_NAME
    model_kwargs = {}
    if json_mode:
        model_kwargs["response_format"] = {"type": "json_object"}

    logger.debug(f"Initializing LLM: {model_to_use} | Temp: {temperature} | Async: True")

    return ChatOpenAI(
        model=model_to_use,
        temperature=temperature,
        api_key=settings.API_KEY.get_secret_value(),
        base_url=settings.BASE_URL,
        streaming=streaming,
        max_retries=settings.MAX_RETRIES,
        request_timeout=settings.TIMEOUT_SECONDS,
        model_kwargs=model_kwargs,
    )

@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:

    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.API_KEY.get_secret_value(),
        base_url=settings.BASE_URL,
        check_embedding_ctx_length=False # Disable check for local models to avoid errors
    )