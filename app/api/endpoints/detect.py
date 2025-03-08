from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.model_loader import get_model
from app.utils.image_utils import process_image
import cv2
import numpy as np

router = APIRouter()

@router.post("/{model_id}/detect")
async def detect_image(model_id: int, file: UploadFile = File(...)):
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Đọc file ảnh
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Thực hiện detection
    results = model(img)

    # Xử lý kết quả
    detection_results = process_image(results)

    return {"results": detection_results}