from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Model
from app.services.model_loader import get_model
import cv2
import numpy as np
import base64
import json

from app.utils.image_utils import process_image

router = APIRouter()


@router.websocket("/ws/{model_id}/detect")
async def websocket_detect(websocket: WebSocket, model_id: int):
    await websocket.accept()

    try:
        # Khởi tạo session database
        db_generator = get_db()
        db = next(db_generator)

        # Kiểm tra xem model có tồn tại trong database không
        model_record = db.query(Model).filter(Model.id == model_id).first()
        if not model_record:
            await websocket.send_json({"error": f"Model with ID {model_id} not found in database"})
            await websocket.close()
            return

        model_info = {
            "id": model_record.id,
            "name": model_record.name,
            "version": model_record.version
        }

        # Lấy model từ bộ nhớ hoặc load nếu chưa có
        model = get_model(model_id)
        if not model:
            await websocket.send_json({"error": f"Failed to load model with ID {model_id}"})
            await websocket.close()
            return

        # Gửi thông báo kết nối thành công và thông tin model
        await websocket.send_json({"status": "connected", "model_info": model_info})

        while True:
            try:
                # Nhận frame từ client
                data = await websocket.receive_text()

                # Kiểm tra nếu client gửi lệnh đóng kết nối
                if data == "close":
                    break

                img_data = base64.b64decode(data)
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Thực hiện detection
                results = model(img)
                detection_results = process_image(results)

                # Gửi kết quả về client
                await websocket.send_json({"model_info": model_info, "results": detection_results})
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})

    except Exception as e:
        await websocket.send_json({"error": f"Server error: {str(e)}"})
    finally:
        # Đảm bảo đóng kết nối websocket
        if db_generator:
            try:
                db_generator.close()
            except:
                pass

        try:
            await websocket.close()
        except:
            pass