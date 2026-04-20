from fastapi import HTTPException, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class NotFoundException(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail

class ConflictException(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail

class AuthenticationException(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail

class AuthorizationException(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail

def _error_response(status_code: int, error: str, path: str) -> JSONResponse:
    """Single place that builds all the error messages in the application."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "status_code": status_code,
            "path": path
        }
    )

def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles all HTTP Exception error's e.g. 404, 403 raised anywhere in the app."""
    assert isinstance(exc, HTTPException)
    return _error_response(
        status_code=exc.status_code,
        error=exc.detail,
        path=str(request.url.path)
    )

def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles all pydantic validation errors e.g. Missing fields, wrong types."""
    assert isinstance(exc, RequestValidationError)
    errors = []
    for e in exc.errors():
        location = " -> ".join(str(l) for l in e["loc"] if l != "body")
        errors.append(f"{location}: {e['msg']}")

    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error="; ".join(errors),
        path=str(request.url.path)
    )

def not_found_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, NotFoundException)
    return _error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        error=exc.detail,
        path=str(request.url.path)
    )

def conflict_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ConflictException)
    return _error_response(
        status_code=status.HTTP_409_CONFLICT,
        error=exc.detail,
        path=str(request.url.path)
    )

def authentication_exception(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AuthenticationException)
    return _error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error=exc.detail,
        path=str(request.url.path)
    )

def authorization_exception(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AuthorizationException)
    return _error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        error=exc.detail,
        path=str(request.url.path)
    )

def unhandled_exception_handler(request: Request, _: Exception) -> JSONResponse:
    """Safety net - catches any unexpected exception that slips through"""
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="An unexpected error occured",
        path=str(request.url.path)
    )

def register_exception_handlers(app: FastAPI) -> None:
    """Call this once in the main app file to register all handlers"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(ConflictException, conflict_exception_handler)
    app.add_exception_handler(AuthenticationException, authentication_exception)
    app.add_exception_handler(AuthorizationException, authorization_exception)
