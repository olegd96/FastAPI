from sqlalchemy import JSON, ForeignKey, Integer, Column, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base

class Users(Base):
    __tablename__= "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str]
    hashed_password: Mapped[str]

    bookings: Mapped[list["Bookings"]] = relationship(back_populates="user")

    def __str__(self):
        return f"Пользователь {self.email}"