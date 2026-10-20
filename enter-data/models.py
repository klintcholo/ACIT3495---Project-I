
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Grade(db.Model):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[str] = mapped_column(db.String(50), nullable=False)
    course: Mapped[str] = mapped_column(db.String(50), nullable=False)
    grade: Mapped[float] = mapped_column(nullable=False)
