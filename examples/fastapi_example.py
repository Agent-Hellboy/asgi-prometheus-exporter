from fastapi import FastAPI, HTTPException

from asgi_prometheus_exporter import PrometheusMiddleware

app = FastAPI()

# Add the middleware
app.add_middleware(PrometheusMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/slow")
async def slow_endpoint():
    import asyncio

    await asyncio.sleep(1)  # Simulate a slow endpoint
    return {"message": "This was slow"}


@app.get("/error")
async def error_endpoint():
    raise HTTPException(status_code=500, detail="There is an error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
