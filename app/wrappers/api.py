import json
import traceback
from collections.abc import Awaitable, Callable
from functools import wraps

from fastapi.responses import JSONResponse

from app.exceptions.base import BaseHTTPException


def api_exception_handler(fn: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            result = await fn(*args, **kwargs)
            if isinstance(result, tuple):
                data, code = result
            else:
                data = result
                code = 200

            return {
                "status": "success",
                "code": code,
                "data": json.loads(data.model_dump_json()) if hasattr(data, "model_dump_json") else data
            }

        except BaseHTTPException as exc:
            error_response = exc.to_error_response()
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "code": exc.status_code,
                    "error": error_response.model_dump()
                }
            )

        except Exception:
            traceback.print_exc()

            unknown_error = BaseHTTPException()
            error_response = unknown_error.to_error_response()
            return JSONResponse(
                status_code=unknown_error.status_code,
                content={
                    "status": "error",
                    "code": unknown_error.status_code,
                    "error": error_response.model_dump()
                }
            )

    return wrapper