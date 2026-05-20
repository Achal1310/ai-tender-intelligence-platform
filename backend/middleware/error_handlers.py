import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def value_error_handler(_: Request, exc: ValueError):
        logger.warning("Validation/runtime value error: %s", exc)
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def generic_error_handler(_: Request, exc: Exception):
        logger.exception("Unhandled server error")
        return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})
