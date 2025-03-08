from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Model
from app.services.model_loader import get_model
from app.utils.image_utils import process_image
import cv2
import numpy as np

router = APIRouter()


@router.post("/{model_id}/detect")
async def detect_image(model_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Kiểm tra xem model có tồn tại trong database không
    model_record = db.query(Model).filter(Model.id == model_id).first()
    if not model_record:
        raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found in database")

    # Lấy model từ bộ nhớ hoặc load nếu chưa có
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=500, detail=f"Failed to load model with ID {model_id}")

    # Đọc file ảnh
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Thực hiện detection
    results = model(img)

    # Xử lý kết quả
    detection_results = process_image(results)

    return {
        "model_info": {
            "id": model_record.id,
            "name": model_record.name,
            "version": model_record.version
        },
        "results": detection_results
    }