from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    version = Column(String)
    model_metadata = Column(String)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    uploader = Column(String)