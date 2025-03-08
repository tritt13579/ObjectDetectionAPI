from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.model_loader import get_model
from app.utils.video_utils import process_video
import cv2
import numpy as np

router = APIRouter()

@router.post("/{model_id}/detect-video")
async def detect_video(model_id: int, file: UploadFile = File(...)):
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Lưu file video tạm thời
    with open("temp_video.mp4", "wb") as buffer:
        buffer.write(await file.read())

    # Mở video
    cap = cv2.VideoCapture("temp_video.mp4")
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
    return {"results": results}