# ASGI Prometheus Exporter

A middleware for ASGI applications that exports Prometheus metrics. This middleware is compatible with any ASGI framework (Django, FastAPI, Starlette, etc.).


- Django (with Django ASGI)
- FastAPI 
- Starlette
- Quart
- Sanic
- Any other ASGI-compatible framework

Tested with FastAPI 

## Features

- Request duration metrics
- Request count metrics
- Response status code metrics
- Custom metrics support (TODO)
- Compatible with any ASGI framework (UNDER EVALUATION)
- Easy to integrate

## Installation

```bash
pip install asgi-prometheus-exporter
```

## Usage

### Basic Usage with FastAPI

```python
from fastapi import FastAPI
from asgi_prometheus_exporter import PrometheusMiddleware

app = FastAPI()
app.add_middleware(PrometheusMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Usage with Django

In your Django project's `asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from asgi_prometheus_exporter import PrometheusMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Get the Django ASGI application
django_asgi_app = get_asgi_application()

# Wrap it with the Prometheus middleware
application = PrometheusMiddleware(
    django_asgi_app,
    metrics_path="/metrics",  # Optional: customize metrics endpoint
    custom_labels={
        "app": "django_app",
        "environment": "production"
    }
)
```

Then in your `settings.py`:
```python
ASGI_APPLICATION = 'myproject.asgi.application'
```

### Usage with Starlette

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from asgi_prometheus_exporter import PrometheusMiddleware

app = Starlette()
app.add_middleware(PrometheusMiddleware)

@app.route("/")
async def homepage(request):
    return JSONResponse({"message": "Hello World"})
```

### Custom Metrics Endpoint

By default, metrics are exposed at `/metrics`. You can customize this by passing the `metrics_path` parameter:

```python
app.add_middleware(
    PrometheusMiddleware,
    metrics_path="/custom/metrics/path"
)
```

### Custom Labels

You can add custom labels to your metrics:

```python
app.add_middleware(
    PrometheusMiddleware,
    custom_labels={
        "app": "myapp",
        "environment": "production"
    }
)
```

## Available Metrics

The middleware exposes the following metrics:

- `asgi_http_requests_total`: Total number of HTTP requests
- `asgi_http_request_duration_seconds`: HTTP request duration in seconds
- `asgi_http_requests_in_progress`: Number of HTTP requests in progress
- `asgi_http_responses_total`: Total number of HTTP responses by status code

## Running with Different ASGI Servers

### Uvicorn
```bash
uvicorn myproject.asgi:application
```

### Daphne (Django)
```bash
daphne myproject.asgi:application
```

### Hypercorn
```bash
hypercorn myproject.asgi:application
```

## License

MIT License 
