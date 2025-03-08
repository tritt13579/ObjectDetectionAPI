from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.auth_middleware import AuthMiddleware
from app.api.endpoints import model
from app.api.endpoints import detect, detect_video, websocket

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các domain truy cập
    allow_credentials=True,  # Cho phép gửi cookie và thông tin xác thực
    allow_methods=["*"],  # Cho phép tất cả các phương thức HTTP (GET, POST, PUT, DELETE, v.v.)
    allow_headers=["*"],  # Cho phép tất cả các headers
)

# Thêm middleware
app.add_middleware(AuthMiddleware)

app.include_router(model.router, prefix="/api")
app.include_router(detect.router, prefix="/api")
app.include_router(detect_video.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")

@app.get("/test")
async def test():
    return {"message": "API Key is valid"}