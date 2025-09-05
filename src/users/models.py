from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ARRAY, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from config.models import Base


# class UserPlaceHistory(Base):
#     __tablename__ = "user_place_history"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     place_id = Column(Integer, ForeignKey('places.id'), nullable=False)
#     show_count = Column(Integer, default=0)
#     liked = Column(Boolean, default=False)
#     disliked = Column(Boolean, default=False)
#     saved = Column(Boolean, default=False)
#     last_shown = Column(DateTime, default=datetime.now)
#     created_at = Column(DateTime, default=datetime.now)
#
#     user = relationship("User", back_populates="place_history")
#     place = relationship("Place")
#
#
# class UserFeedState(Base):
#     __tablename__ = "user_feed_state"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
#     current_category = Column(String)  # Текущая выбранная категория
#     search_radius = Column(Float, default=5.0)  # Радиус поиска в км
#     last_place_id = Column(Integer, ForeignKey('places.id'))  # Последнее показанное место
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
#
#     user = relationship("User", back_populates="feed_state")
#     last_place = relationship("Place")


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

    # place_history = relationship("UserPlaceHistory", back_populates="user")
    # feed_state = relationship("UserFeedState", back_populates="user", uselist=False)
