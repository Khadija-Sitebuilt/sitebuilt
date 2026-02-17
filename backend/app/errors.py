# app/errors.py
import uuid
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(
    *,
    status_code: int,
    error: str,
    message: str,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "detail": message,  # Keep 'detail' for compatibility
            "message": message,
            "request_id": str(uuid.uuid4()),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        status_code=exc.status_code,
        error="HTTP_ERROR",
        message=str(exc.detail),
    )


async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors. Check if it's a missing header (X-User-Id)
    and return 403 instead of 422.
    """
    errors = exc.errors()
    
    # Check if error is due to missing X-User-Id header
    for error in errors:
        error_type = error.get("type")
        # Handle both 'missing' and 'value_error.missing' error types
        if error_type in ["missing", "value_error.missing"]:
            locations = error.get("loc", [])
            # locations is a tuple like ('header', 'X-User-Id')
            if len(locations) >= 2 and locations[0] == "header":
                header_name = locations[1]
                if header_name in ["X-User-Id", "x_user_id", "x-user-id"]:
                    return error_response(
                        status_code=403,
                        error="FORBIDDEN",
                        message="X-User-Id header is required",
                    )
    
    # Default validation error response
    return error_response(
        status_code=422,
        error="VALIDATION_ERROR",
        message="Request validation failed",
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(
        status_code=500,
        error="INTERNAL_SERVER_ERROR",
        message="Something went wrong",
    )
