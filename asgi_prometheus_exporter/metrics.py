from prometheus_client import Counter, Gauge, Histogram

# Define metrics
HTTP_REQUESTS_TOTAL = Counter(
    "asgi_http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "asgi_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status_code"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    ),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "asgi_http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "path"],
)

HTTP_RESPONSES_TOTAL = Counter(
    "asgi_http_responses_total",
    "Total number of HTTP responses",
    ["method", "path", "status_code"],
)
