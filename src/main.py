from fastapi import FastAPI

# Middlawares
from fastapi.middleware.cors import CORSMiddleware

# Documentation
from fastapi.openapi.utils import get_openapi
from src.routes import router

# App instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
