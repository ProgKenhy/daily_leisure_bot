from sqlalchemy import Column, Integer, String, Float, Text, Boolean, Time, ARRAY, Enum
from enum import Enum as PyEnum
from config.models import Base

class PlaceCategory(PyEnum):
    PARK = "park"
    MUSEUM = "museum"
    CAFE = "cafe"
    RESTAURANT = "restaurant"
    BAR = "bar"
    GALLERY = "gallery"
    THEATER = "theater"
    CINEMA = "cinema"
    SHOP = "shop"
    SPORT = "sport"
    NATURE = "nature"
    HISTORIC = "historic"
    OTHER = "other"

class WeekDay(PyEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(PlaceCategory), default=PlaceCategory.OTHER)

    address = Column(String(300))
    loc_lat = Column(Float, nullable=False)
    loc_lon = Column(Float, nullable=False)

    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)

    working_days = Column(ARRAY(Enum(WeekDay)))

    image_url = Column(String(500))
    local_image_path = Column(String(300))

    phone = Column(String(20))
    website = Column(String(200))

    rating = Column(Float, default=0.0)
    price_level = Column(Integer)  # 1-3

    is_active = Column(Boolean, default=True)

    def is_open_now(self):
        """Проверяет, открыто ли место сейчас"""
        # Логика будет в сервисном слое
        pass

    def get_working_hours_str(self):
        """Возвращает строку с временем работы"""
        if self.opening_time and self.closing_time:
            return f"{self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        return "Время работы не указано"

    def get_working_days_str(self):
        """Возвращает строку с днями работы на русском"""
        if self.working_days:
            days_map = {
                WeekDay.MONDAY: "Пн",
                WeekDay.TUESDAY: "Вт",
                WeekDay.WEDNESDAY: "Ср",
                WeekDay.THURSDAY: "Чт",
                WeekDay.FRIDAY: "Пт",
                WeekDay.SATURDAY: "Сб",
                WeekDay.SUNDAY: "Вс"
            }
            return ', '.join([days_map[day] for day in self.working_days])
        return "Дни работы не указаны"