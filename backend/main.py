from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import shutil
import uuid
import os
from typing import List

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/check_exists/{serial_number}")
async def check_exists(serial_number: str):
    """
    Check that a temp file of images with this serial doesn't already exists.
    This stops you from being able to upload multiple sets of images at once
    then upload greater than the required number of images
    """
    folder_path = os.path.join(UPLOAD_DIR, serial_number)
    exists = os.path.exists(folder_path)
    return {"exists": exists}


@app.get("/check_uploads/{serial_number}")
async def check_uploads(serial_number: str):
    """
    Check how many images have been uploaded for a given serial number.
    """
    folder_path = os.path.join(UPLOAD_DIR, serial_number)

    if not os.path.exists(folder_path):
        return {"status": "folder does not exist", "count": 0}

    # Count files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    total_files = len(files)

    expected: int = 277
    if total_files == expected:
        # AT THIS POINT YOU WOULD WRITE TO DB AND THEN CLEAR THIS TEMP DIRECTORY
        # NOTE THAT BECAUSE THIS TEMP DIRECTORY IS CLEARED YOU WOULD HAVE TO MAKE SURE
        # Image data for a given serial doesn't already exist in the DB
        return {"status": "all images uploaded", "count": total_files}
    else:
        return {"status": "incomplete upload", "count": total_files}


@app.post("/upload_batch/")
async def upload_batch(
    serial_number: str = Form(...),
    files: List[UploadFile] = File(...),
):
    """
    Upload multiple images to the 'server'. In this case it actually just writes them to a folder in this project
    however this clearly shows that the images have been transferred correctly.
    """
    uploaded_files = []

    full_upload_dir = os.path.join(UPLOAD_DIR, serial_number)
    os.makedirs(full_upload_dir, exist_ok=True)

    for file in files:
        file_ext: str = file.filename.split(".")[-1]
        file_id: str = f"{uuid.uuid4()}.{file_ext}"
        file_path: str = os.path.join(full_upload_dir, file_id)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append({
            "original_filename": file.filename,
            "stored_filename": file_id,
            "url": f"/image/{file_id}"
        })

    return {"uploaded": uploaded_files}


@app.get("/image/{filename}")
async def get_image(filename: str):
    """
    This is just a test function to display the images you've uploaded. It's not actually required.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "Image not found"}, status_code=404)
    return FileResponse(file_path, media_type="image/jpeg")


@app.get("/")
async def root():
    return {"message": "Batch Image Upload API is running!"}
