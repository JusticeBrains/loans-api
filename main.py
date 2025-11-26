from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from api.router import api_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Loans API", version="1.0.1")

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

app.include_router(api_router)
