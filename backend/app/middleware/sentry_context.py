# app/middleware/sentry_context.py
import sentry_sdk
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SentryContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = request.headers.get("X-User-Id")

        sentry_sdk.set_context(
            "request",
            {
                "method": request.method,
                "path": request.url.path,
            },
        )

        if user_id:
            sentry_sdk.set_user({"id": user_id})

        # Try extracting project_id from path params
        project_id = request.path_params.get("project_id")
        if project_id:
            sentry_sdk.set_tag("project_id", project_id)

        response = await call_next(request)
        return response
