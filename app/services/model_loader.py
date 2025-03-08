from ultralytics import YOLO
from app.core.config import MODEL_DIR
import os
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Model

# Dictionary để lưu các model đã load
loaded_models = {}


def load_model(model_id: int, filename: str = None):
    """Load model từ file và lưu vào dictionary"""
    try:
        # Lấy filename từ database nếu không được cung cấp
        if filename is None:
            db = next(get_db())
            model_record = db.query(Model).filter(Model.id == model_id).first()
            if not model_record:
                raise ValueError(f"Model with id {model_id} not found in database")
            filename = model_record.filename

        model_path = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        model = YOLO(model_path)
        loaded_models[model_id] = model
        print(f"Model {model_id} (file: {filename}) loaded successfully.")
        return True
    except Exception as e:
        print(f"Error loading model {model_id}: {e}")
        return False


def get_model(model_id: int):
    """Lấy model từ dictionary, nếu chưa load thì load lại từ database"""
    model = loaded_models.get(model_id)
    if model is None:
        # Thử load model từ database
        if load_model(model_id):
            return loaded_models.get(model_id)
        return None
    return model


def reload_model(model_id: int):
    """Reload model từ file"""
    if model_id in loaded_models:
        del loaded_models[model_id]
    return load_model(model_id)


def unload_model(model_id: int):
    """Xóa model khỏi bộ nhớ"""
    if model_id in loaded_models:
        del loaded_models[model_id]
        print(f"Model {model_id} unloaded.")
        return True
    return False