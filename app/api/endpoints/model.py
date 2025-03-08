from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.db.models import Model
from app.services.model_loader import load_model
from app.core.config import MODEL_DIR
import os
import shutil
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/model/upload")
async def upload_model(
    file: UploadFile = File(...),
    name: str = Form(...),
    version: str = Form("1.0"),
    metadata: str = Form(""),
    uploader: str = Form("admin"),
    db: Session = Depends(get_db)
):
    # Kiểm tra model có trùng name + version không
    existing_model = db.query(Model).filter(Model.name == name, Model.version == version).first()
    if existing_model:
        raise HTTPException(status_code=400, detail=f"Model with name '{name}' and version '{version}' already exists.")

    # Xử lý lưu file với tên duy nhất
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1] if "." in original_filename else ""
    unique_filename = f"{name.replace(' ', '_')}_{version}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = os.path.join(MODEL_DIR, unique_filename)

    # Tạo thư mục nếu chưa có
    os.makedirs(MODEL_DIR, exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Thêm model vào database
        new_model = Model(
            name=name,
            version=version,
            filename=unique_filename,
            original_filename=original_filename,
            model_metadata=metadata,
            uploader=uploader
        )
        db.add(new_model)
        db.commit()
        db.refresh(new_model)

        # Load model vào bộ nhớ
        load_model(new_model.id, unique_filename)

        return {
            "message": "Model uploaded and loaded successfully",
            "model_id": new_model.id,
            "name": name,
            "version": version,
            "filename": unique_filename
        }
    except IntegrityError:
        if os.path.exists(file_path):
            os.remove(file_path)  # Xóa file nếu lỗi DB
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error occurred while saving model information")
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)  # Xóa file nếu lỗi hệ thống
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/list-model")
async def list_models(db: Session = Depends(get_db)):
    models = db.query(Model).all()
    return [
        {
            "id": model.id,
            "name": model.name,
            "version": model.version,
            "upload_time": model.upload_time,
            "original_filename": model.original_filename,
            "model_metadata": model.model_metadata,
            "uploader": model.uploader
        } for model in models
    ]


@router.delete("/model/{model_id}")
async def delete_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found")

    # Xóa file model từ thư mục
    file_path = os.path.join(MODEL_DIR, model.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Xóa bản ghi từ database
    db.delete(model)
    db.commit()

    return {"message": f"Model {model.name} (ID: {model_id}) deleted successfully"}