from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    version = Column(String)
    filename = Column(String, unique=True)
    original_filename = Column(String)
    model_metadata = Column(String)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    uploader = Column(String)

    __table_args__ = (UniqueConstraint('name', 'version', name='unique_name_version'),)