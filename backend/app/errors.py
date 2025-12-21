# app/errors.py
import uuid
from fastapi import Request, HTTPException
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


async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(
        status_code=500,
        error="INTERNAL_SERVER_ERROR",
        message="Something went wrong",
    )
