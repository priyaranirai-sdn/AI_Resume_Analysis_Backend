from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

def create_error_response(status_code: int, message: str, details: dict = None):
    """Create a standardized error response"""
    error_response = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    if details:
        error_response["details"] = details
    return error_response

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            status_code=422,
            message="Validation error",
            details={"validation_errors": errors}
        )
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=400,
        content=create_error_response(
            status_code=400,
            message="Database integrity error - duplicate or invalid data",
            details={"error": str(exc.orig) if hasattr(exc, 'orig') else str(exc)}
        )
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            message="Internal server error",
            details={"error": "An unexpected error occurred"}
        )
    )
