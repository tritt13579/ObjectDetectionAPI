from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Model
from app.services.model_loader import get_model
from app.utils.video_utils import process_video
import cv2
import os
import uuid

router = APIRouter()


@router.post("/{model_id}/detect-video")
async def detect_video(model_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Kiểm tra xem model có tồn tại trong database không
    model_record = db.query(Model).filter(Model.id == model_id).first()
    if not model_record:
        raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found in database")

    # Lấy model từ bộ nhớ hoặc load nếu chưa có
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=500, detail=f"Failed to load model with ID {model_id}")

    # Tạo tên file tạm thời với UUID để tránh xung đột
    temp_filename = f"temp_video_{uuid.uuid4()}.mp4"
    temp_path = os.path.join("temp", temp_filename)

    # Đảm bảo thư mục temp tồn tại
    os.makedirs("temp", exist_ok=True)

    try:
        # Lưu file video tạm thời
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Mở video
        cap = cv2.VideoCapture(temp_path)
        results = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Thực hiện detection trên frame
            frame_results = model(frame)
            # Xử lý kết quả
            frame_detection = process_video(frame_results)
            results.append(frame_detection)

        cap.release()

        return {
            "model_info": {
                "id": model_record.id,
                "name": model_record.name,
                "version": model_record.version
            },
            "results": results
        }
    finally:
        # Xóa file tạm sau khi xử lý xong
        if os.path.exists(temp_path):
            os.remove(temp_path)