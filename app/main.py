from fastapi import FastAPI
from app.middlewares.auth_middleware import AuthMiddleware
from app.api.endpoints import model
from app.api.endpoints import detect, detect_video, websocket

app = FastAPI()

# Thêm middleware
app.add_middleware(AuthMiddleware)

app.include_router(model.router, prefix="/api")
app.include_router(detect.router, prefix="/api")
app.include_router(detect_video.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")

@app.get("/test")
async def test():
    return {"message": "API Key is valid"}