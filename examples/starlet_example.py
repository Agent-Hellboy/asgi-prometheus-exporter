from starlette.applications import Starlette
from starlette.responses import JSONResponse

from asgi_prometheus_exporter import PrometheusMiddleware

app = Starlette()
app.add_middleware(PrometheusMiddleware)


@app.route("/")
async def homepage(request):
    return JSONResponse({"message": "Hello World"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
