import time

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    HTTP_RESPONSES_TOTAL,
)


class PrometheusMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        metrics_path: str = "/metrics",
        custom_labels: dict[str, str] | None = None,
    ) -> None:
        self.app = app
        self.metrics_path = metrics_path
        self.custom_labels = custom_labels or {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        method = scope["method"]

        # Handle metrics endpoint
        if path == self.metrics_path:
            if method == "GET":
                response = Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
                await response(scope, receive, send)
                return
            else:
                # Return 405 Method Not Allowed for non-GET requests
                response = Response(
                    "Method not allowed", status_code=405, media_type="text/plain"
                )
                await response(scope, receive, send)
                return

        # Start timing the request
        start_time = time.time()

        # Increment in-progress requests
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()

        # Create a custom send function to intercept the response
        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_code = str(message["status"])

                # Record request metrics
                HTTP_REQUESTS_TOTAL.labels(
                    method=method, path=path, status_code=status_code
                ).inc()

                # Record response metrics
                HTTP_RESPONSES_TOTAL.labels(
                    method=method, path=path, status_code=status_code
                ).inc()

                # Record request duration
                duration = time.time() - start_time
                HTTP_REQUEST_DURATION_SECONDS.labels(
                    method=method, path=path, status_code=status_code
                ).observe(duration)

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Handle any unhandled exceptions
            status_code = "500"
            if isinstance(e, HTTPException):
                status_code = str(e.status_code)

            # Record metrics for the error
            HTTP_REQUESTS_TOTAL.labels(
                method=method, path=path, status_code=status_code
            ).inc()

            HTTP_RESPONSES_TOTAL.labels(
                method=method, path=path, status_code=status_code
            ).inc()

            # Record request duration for the error
            duration = time.time() - start_time
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method, path=path, status_code=status_code
            ).observe(duration)

            raise e
        finally:
            # Decrement in-progress requests
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()

    def _get_path(self, scope: Scope) -> str:
        """Get the path from the scope, handling path parameters."""
        path = scope["path"]
        # If the path contains path parameters (like /users/{user_id}),
        # we should normalize it to avoid cardinality issues
        if "{" in path:
            # This is a simple approach - you might want to implement
            # more sophisticated path parameter handling
            parts = path.split("/")
            normalized_parts = []
            for part in parts:
                if part.startswith("{") and part.endswith("}"):
                    normalized_parts.append("{param}")
                else:
                    normalized_parts.append(part)
            return "/".join(normalized_parts)
        return path
