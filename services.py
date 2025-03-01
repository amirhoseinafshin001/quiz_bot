"""
CRUD opprations and business logic
"""


import random
from typing import Any
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func

from database import AsyncSessionLocal
from models import Game
from models import User
from models import Question
from models import UserGame
from models import UserAnswer
from models import GameStatus


POSITIVE_SCORE = 12
NEGATIVE_SCORE = -4


async def get_or_create_user(user_id: str) -> User:
    """create user if doesn't exist"""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            user = await db.query(User).filter_by(bale_id=user_id).first()
            if not user:
                user = User(bale_id=user_id)
                db.add(user)
                await db.commit()
        return user


async def find_match(user_id: str) -> Game | None:
    """Find a match and start the game"""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(select(Game).where(Game.status == GameStatus.WAITING).with_for_update())
            game = result.scalars().first()

            if game:
                game.status = GameStatus.IN_PROGRESS
                db.add(UserGame(user_id=user_id, game_id=game.id))
            else:
                game = Game(status=GameStatus.WAITING)
                db.add(game)
                db.add(UserGame(user_id=user_id, game_id=game.id))

            await db.commit()
        return game


async def start_game(game_id: str) -> list[Question]:
    """choose random questions for a match"""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(select(Game).where(Game.id == game_id))
            game = result.scalars().first()

            if not game or game.status != GameStatus.WAITING:
                return None

            questions_result = await db.execute(select(Question).order_by(func.random()).limit(5))
            questions = questions_result.scalars().all()
            game.questions = questions
            game.status = GameStatus.IN_PROGRESS
            await db.commit()
        return questions


async def handle_answer(user_id: str, game_id: str, question_id: str, selected_option: str) -> dict[str, Any]:
    """Check user answer and calculate the score"""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            game_result = await db.execute(select(Game).where(Game.id == game_id))
            game = game_result.scalars().first()
            if not game or game.status != GameStatus.IN_PROGRESS:
                return None

            question_result = await db.execute(select(Question).where(Question.id == question_id))
            question = question_result.scalars().first()
            if not question:
                return None

            is_correct = selected_option == question.option1
            user_answer = UserAnswer(
                user_id=user_id,
                game_id=game_id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct,
                answered_at=datetime.utcnow()
            )
            db.add(user_answer)

            user_game_result = await db.execute(
                select(UserGame).where(
                    UserGame.user_id == user_id,
                    UserGame.game_id == game_id
                ))
            user_game = user_game_result.scalars().first()
            if is_correct:
                user_game.score += POSITIVE_SCORE
            else:
                user_game.score += NEGATIVE_SCORE

            await db.commit()
        return {"correct": is_correct, "score": user_game.score}


async def finish_game(game_id: str) -> dict[str, int]:
    """finish the game and record it"""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            result = await db.execute(select(Game).where(Game.id == game_id).options(joinedload(Game.users)))
            game = result.scalars().first()

            if not game or game.status != GameStatus.IN_PROGRESS:
                return None

            game.status = GameStatus.FINISHED
            await db.commit()

            results = {user_game.user_id: user_game.score for user_game in game.users}
        return results



"""async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    A(bs=[B(data="b1"), B(data="b2")], data="a1"),
                    A(bs=[], data="a2"),
                    A(bs=[B(data="b3"), B(data="b4")], data="a3"),
                ]
            )
"""