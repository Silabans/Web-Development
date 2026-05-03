from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from typing import List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    id: Mapped[int] = mapped_column(primary_key=True)

    tasks: Mapped[List["Task"]] = relationship(back_populates="owner")
    last_timer: Mapped[int] = mapped_column(default=25)


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    content: Mapped[str] = mapped_column(nullable=False) # stores the description ofthe task
    priority: Mapped[int] = mapped_column(nullable=True) # stores 1, 2, 3 (priority values)
    due_date: Mapped[str] = mapped_column(nullable=True) # stores the due date
    isCompleted: Mapped[bool] = mapped_column(default=False) # marks the completion of the task

    @property
    def priority_label(self):
        """This function converts the numerical value of the task's priority into its word form."""

        # The dictionary translates the priority values into their word forms for display
        mapping = {1: "Low", 2: "Medium", 3: "High"}

        # This takes the number from the priority attribute and returns its word form
        # from the mapping dictionary. If the numbers are not 1, 2 or 3, it returns "Not Set"
        return mapping.get(self.priority, "Not Set")

    owner: Mapped[User] = relationship(back_populates="tasks")