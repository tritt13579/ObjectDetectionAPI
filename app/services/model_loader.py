from ultralytics import YOLO
from app.core.config import MODEL_DIR
import os

# Dictionary để lưu các model đã load
loaded_models = {}

def load_model(model_id: int, model_path: str):
    """Load model từ file và lưu vào dictionary"""
    try:
        model = YOLO(os.path.join(MODEL_DIR, model_path))
        loaded_models[model_id] = model
        print(f"Model {model_id} loaded successfully.")
    except Exception as e:
        print(f"Error loading model {model_id}: {e}")

def get_model(model_id: int):
    """Lấy model từ dictionary"""
    return loaded_models.get(model_id)