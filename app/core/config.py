from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env
load_dotenv()

# Lấy các biến từ môi trường
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_DIR = os.getenv("MODEL_DIR")