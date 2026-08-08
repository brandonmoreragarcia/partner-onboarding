from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.routers.dev import router as dev_router
from app.routers.sessions import router as sessions_router
from app.schemas import ErrorResponse

app = FastAPI(title="Partner Onboarding API")

# Local dev only: the Vite dev server runs on a different origin (5173) than the API
# (8000), so the browser blocks requests without this. No production deploy in scope.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(dev_router)


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(code=exc.code, message=exc.message).model_dump(by_alias=True),
    )
