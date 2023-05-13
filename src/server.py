from urllib.request import Request
from fastapi import FastAPI
from controllers.trainings_controller import router as training_router
from starlette.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def init_routers(app):
    app.include_router(training_router, prefix="/api/trainings")


app = FastAPI()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

origins = [
    "http://localhost:80",  # adjust this as necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]  # expose your custom header
)

init_routers(app)


@app.get("/")
async def index():
    return {"data": "test"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


