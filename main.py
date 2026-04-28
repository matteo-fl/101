import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import pypdf
from docx import Document
from dotenv import load_dotenv
from llm_service import generate_structure
from image_service import generate_image
from pptx_generator import create_pptx

load_dotenv()

app = FastAPI(title="AI PPTX Generator")
os.makedirs("uploads", exist_ok=True)

# CORS - разрешаем запросы с React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку uploads как статическую (для доступа к картинкам)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Шаблонизатор (если нужен старый HTML)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def extract_text(file: UploadFile) -> str:
    """Извлечение текста из PDF/DOCX"""
    if file is None or file.filename == "":
        return ""
    
    path = os.path.join("uploads", file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    text = ""
    try:
        if file.filename.lower().endswith(".pdf"):
            with open(path, "rb") as f:
                reader = pypdf.PdfReader(f)
                text = "\n".join([p.extract_text() or "" for p in reader.pages])
        elif file.filename.lower().endswith(".docx"):
            doc = Document(path)
            text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    
    return text[:3000]

@app.post("/api/generate")
async def generate(
    prompt: str = Form(...),
    num_slides: int = Form(10),
    style: str = Form("Современный"),
    tone: str = Form("Профессиональный"),
    file: UploadFile = File(None)
):
    """Генерация презентации"""
    try:
        doc_text = ""
        if file and file.filename:
            doc_text = extract_text(file)
        
        # Генерируем структуру слайдов
        structure = generate_structure(prompt, doc_text, num_slides, style, tone)
        
        # Генерируем изображения для каждого слайда
        for i, slide in enumerate(structure):
            if slide.get("image_prompt"):
                generate_image(slide["image_prompt"], f"uploads/img_{i}.png")
        
        # Создаем PPTX
        pptx_path = "uploads/result.pptx"
        create_pptx(structure, pptx_path)
        
        return JSONResponse({"slides": structure, "message": "Готово!"})
    
    except Exception as e:
        print(f"Error in generate: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), slide_index: int = Form(...)):
    """Загрузка пользовательского изображения для слайда"""
    try:
        # Сохраняем файл
        file_path = f"uploads/slide_{slide_index}_custom.png"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Изображение загружено: {file_path}")
        
        return JSONResponse({
            "message": "Изображение загружено",
            "file_path": file_path
        })
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/regenerate-image")
async def regenerate_image(prompt: str = Form(...), slide_index: int = Form(...)):
    """Перегенерация изображения через AI"""
    try:
        file_path = f"uploads/img_{slide_index}.png"
        
        # Генерируем новое изображение
        result = generate_image(prompt, file_path)
        
        if result:
            print(f"✅ Изображение перегенерировано: {file_path}")
            return JSONResponse({
                "message": "Изображение сгенерировано",
                "file_path": file_path
            })
        else:
            return JSONResponse({"error": "Не удалось сгенерировать"}, status_code=500)
            
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download")
async def download():
    """Скачивание готовой презентации"""
    pptx_path = "uploads/result.pptx"
    if not os.path.exists(pptx_path):
        return JSONResponse({"error": "Файл ещё не сгенерирован"}, status_code=404)
    
    return FileResponse(
        pptx_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename='presentation.pptx'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)