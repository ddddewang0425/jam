from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    return {
        "filename": file.filename,
        "url": f"http://localhost:8000/uploads/{file.filename}"  # ngrok로 바꿔야 함
    }

@app.get("/")
async def main():
    content = """
    <form action="/upload/" enctype="multipart/form-data" method="post">
    <input name="file" type="file">
    <input type="submit">
    </form>
    """
    return HTMLResponse(content=content)

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")