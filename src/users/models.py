from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ARRAY, DateTime

from config.models import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    interests = Column(ARRAY(String), default=[])
    loc_lat = Column(Float)
    loc_lon = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
