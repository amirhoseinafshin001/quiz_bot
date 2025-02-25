"""
Database models are here
"""


from uuid import uuid4
from typing import List
from enum import Enum

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import Column




class Base(DeclarativeBase):
    pass



association_table = Table(
    # question-game association
    "association_table",
    Base.metadata,
    Column("game_id", ForeignKey("games.id"), primary_key=True),
    Column("question_id", ForeignKey("questions.id"), primary_key=True),
)



class QuestionCategory(Enum):
    # what ever the categories are
    SCIENCE = "science"
    HISTORY = "history"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    GEOGRAPHY = "geography"



class User(Base):
    __tablename__ = "users"

    bale_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        unique = True
    )

    total_score: Mapped[int] = mapped_column(
        default=0
    )

    games: Mapped[List["UserGame"]] = relationship(
        back_populates="user"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)




class UserGame(Base):
    # Associates users and games
    # Also represents each player's score from each game
    __tablename__ = "usergames"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        unique=True
    )
    score: Mapped[int] = mapped_column(
        default=0
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.bale_id")
    )
    user: Mapped["User"] = relationship(
        back_populates="games"
    )
    
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id")
    )
    game: Mapped["Game"] = relationship(
        back_populates="users"
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid4()))
        super().__init__(**kwargs)




class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        unique=True
    )

    users: Mapped[List["UserGame"]] = relationship(
        back_populates="game"
    )

    questions: Mapped[List["Question"]] = relationship(
        secondary=association_table,
        back_populates="games"
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid4()))
        super().__init__(**kwargs)




class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        unique=True,
    )

    text: Mapped[str] = mapped_column(
        String
    )
    category: Mapped[QuestionCategory] = mapped_column(
        SQLEnum(QuestionCategory),
        nullable=False
    )
    
    option1: Mapped[str] = mapped_column(String) # By convention, this is the Correct Option.
    option2: Mapped[str] = mapped_column(String)
    option3: Mapped[str] = mapped_column(String)
    option4: Mapped[str] = mapped_column(String)

    games: Mapped[List["Game"]] = relationship(
        secondary=association_table,
        back_populates="questions"
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid4()))
        super().__init__(**kwargs)
