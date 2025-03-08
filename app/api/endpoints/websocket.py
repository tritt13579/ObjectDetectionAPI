from fastapi import APIRouter, WebSocket
from app.services.model_loader import get_model
import cv2
import numpy as np
import base64

from app.utils.image_utils import process_image

router = APIRouter()

@router.websocket("/ws/{model_id}/detect")
async def websocket_detect(websocket: WebSocket, model_id: int):
    await websocket.accept()
    model = get_model(model_id)
    if not model:
        await websocket.send_text("Model not found")
        await websocket.close()
        return

    while True:
        try:
            # Nhận frame từ client
            data = await websocket.receive_text()
            img_data = base64.b64decode(data)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Thực hiện detection
            results = model(img)
            detection_results = process_image(results)

            # Gửi kết quả về client
            await websocket.send_json(detection_results)
        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break