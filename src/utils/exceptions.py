from fastapi import Request, status
from fastapi.responses import JSONResponse

class AgentOSError(Exception):
    """Base exception for all Agent OS errors."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class ConfigurationError(AgentOSError):
    """Raised when .env or config is invalid."""
    pass

class LLMGenerationError(AgentOSError):
    """Raised when the LLM provider fails or returns invalid format."""
    pass

class ToolExecutionError(AgentOSError):
    """Raised when a tool (e.g., Docling, Search) fails."""
    pass

class SecurityError(AgentOSError):
    """Raised by Guardrails when PII or unsafe content is detected."""
    pass

# --- FastAPI Exception Handlers ---
# You will register these in src/scaffold/main.py later

async def agent_os_exception_handler(request: Request, exc: AgentOSError):
    """
    Converts our custom exceptions into clean JSON responses.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        },
    )

async def security_exception_handler(request: Request, exc: SecurityError):
    """
    Specific handler for Security errors (Return 403 Forbidden).
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "SecurityViolation",
            "message": exc.message
        },
    )