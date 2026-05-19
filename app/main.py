from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from .database import init_db
from .router import router
from .ui import HTML_UI

load_dotenv()
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="HashGuard",
        description="AI-enhanced file integrity monitoring — SHA-256 hashing + Isolation Forest anomaly detection",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index():
        return HTML_UI

    return app


app = create_app()
