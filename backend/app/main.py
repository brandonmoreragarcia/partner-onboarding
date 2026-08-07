from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.routers.sessions import router as sessions_router
from app.schemas import ErrorResponse

app = FastAPI(title="Partner Onboarding API")

app.include_router(sessions_router)


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(code=exc.code, message=exc.message).model_dump(by_alias=True),
    )
