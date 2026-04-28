from fastapi import FastAPI
from app.routes import generate, presentation, upload

app = FastAPI()

app.include_router(generate.router)
app.include_router(presentation.router)
app.include_router(upload.router)