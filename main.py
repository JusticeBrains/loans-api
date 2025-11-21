from fastapi import FastAPI

from api.router import api_router


app = FastAPI(title="Loans API", version="1.0.1")

app.include_router(api_router)
