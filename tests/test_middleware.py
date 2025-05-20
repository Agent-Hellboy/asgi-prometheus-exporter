import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from asgi_prometheus_exporter import PrometheusMiddleware


@pytest.fixture
def app():
    app = Starlette()
    app.add_middleware(PrometheusMiddleware)

    @app.route("/")
    async def homepage(request):
        return JSONResponse({"message": "Hello World"})

    @app.route("/slow")
    async def slow_endpoint(request):
        import asyncio

        await asyncio.sleep(0.1)  # Simulate a slow endpoint
        return JSONResponse({"message": "This was slow"})

    @app.route("/error")
    async def error_endpoint(request):
        raise ValueError("This is an error")

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text

    # Check if our metrics are present
    assert "asgi_http_requests_total" in content
    assert "asgi_http_request_duration_seconds" in content
    assert "asgi_http_requests_in_progress" in content
    assert "asgi_http_responses_total" in content


def test_normal_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

    # Check metrics after request
    metrics = client.get("/metrics").text
    assert (
        'asgi_http_requests_total{method="GET",path="/",status_code="200"}' in metrics
    )


def test_slow_endpoint(client):
    response = client.get("/slow")
    assert response.status_code == 200
    assert response.json() == {"message": "This was slow"}

    # Check metrics after request
    metrics = client.get("/metrics").text
    assert (
        'asgi_http_request_duration_seconds_bucket{le="+Inf",method="GET",path="/slow",status_code="200"}'
        in metrics
    )


def test_error_endpoint(client):
    try:
        response = client.get("/error")
        assert response.status_code == 500
    except Exception:
        pass

    # Check metrics after request
    metrics = client.get("/metrics").text
    assert (
        'asgi_http_requests_total{method="GET",path="/error",status_code="500"}'
        in metrics
    )
