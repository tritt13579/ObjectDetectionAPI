from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Model
from app.services.model_loader import load_model
from app.core.config import MODEL_DIR
import os
import shutil

router = APIRouter()

@router.post("/model/upload")
async def upload_model(file: UploadFile = File(...), name: str = "New Model", version: str = "1.0", metadata: str = "", uploader: str = "admin", db: Session = Depends(get_db)):
    # Lưu file model vào thư mục MODEL_DIR
    file_path = os.path.join(MODEL_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Lưu thông tin model vào database
    new_model = Model(name=name, version=version, metadata=metadata, uploader=uploader)
    db.add(new_model)
    db.commit()
    db.refresh(new_model)

    # Load model vào bộ nhớ
    load_model(new_model.id, file.filename)

    return {"message": "Model uploaded and loaded successfully", "model_id": new_model.id}

@router.get("/list-model")
async def list_models(db: Session = Depends(get_db)):
    models = db.query(Model).all()
    return [{"id": model.id, "name": model.name, "version": model.version, "upload_time": model.upload_time} for model in models]