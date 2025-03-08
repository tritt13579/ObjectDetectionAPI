from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Tạo engine kết nối đến cơ sở dữ liệu
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Tạo session để tương tác với cơ sở dữ liệu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các model
Base = declarative_base()

# Dependency để lấy session trong các endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()