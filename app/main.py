from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_versionizer.versionizer import Versionizer

from app.api.routers import all_routers
from app.config.main import settings
from app.exceptions.base import BaseHTTPException
from app.mock.mock import init_app
from app.schemas.base import ErrorEnvelopeModel

openapi_url = None
redoc_url = None

if settings.VISIBILITY_DOCUMENTATION is True:
    openapi_url = "/openapi.json"
    redoc_url = "/redoc"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.MODE == "TEST":
        await init_app()
    yield


app = FastAPI(
    title="Construct API",
    lifespan=lifespan,
    openapi_url=openapi_url,
    redoc_url=redoc_url
)

for router in all_routers:
    app.include_router(router)

origins = ["https://constructioncms.ru", "http://constructioncms.ru", settings.WEB_APP_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


@app.exception_handler(BaseHTTPException)
async def base_service_exception_handler(request: Request, exc: BaseHTTPException):
    error_envelope = ErrorEnvelopeModel(
        status="error",
        code=exc.status_code,
        error=exc.to_error_response(),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope.model_dump()
    )

versions = Versionizer(
    app=app, prefix_format="/api/v{major}", semantic_version_format="{major}", sort_routes=True
).versionize()


@app.get("/health", include_in_schema=False)
def health_check() -> dict:
    """Для проверки жизни приложения"""
    return {"status": "healthy"}