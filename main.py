from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router


settings = get_settings()


app = FastAPI(
    title=settings.app_name,

    description=(
        "AI comic story creator "
        "using Gemini and image generation."
    ),

    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            settings.static_dir
        )
    ),
    name="static"
)


app.mount(
    "/exports",
    StaticFiles(
        directory=str(
            settings.exports_dir
        )
    ),
    name="exports"
)


app.include_router(
    router
)


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": settings.app_name
    }