import sys
import logging
from loguru import logger
from src.llm.config import settings

class InterceptHandler(logging.Handler):
    """
    Redirects standard logging messages (from libraries) to Loguru.
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """
    Configures the global logger.
    """
    # 1. Remove default handlers
    logger.remove()

    # 2. Determine format based on Environment
    # Development: Readable colors
    # Production: JSON structured logs (better for CloudWatch/Datadog)
    if settings.ENV == "production":
        logger.add(
            sys.stdout,
            serialize=True, 
            level=settings.LOG_LEVEL,
            enqueue=True # Async safe
        )
    else:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True
        )

    # 3. Intercept standard library logs (e.g. uvicorn, langchain)
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Silence noisy libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger.info(f"Logger initialized in {settings.ENV} mode")