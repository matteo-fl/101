from fastapi import APIRouter, UploadFile
from app.services.parser_service import extract_text

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile):
    text = extract_text(file)
    return {"text": text}