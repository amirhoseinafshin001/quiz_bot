import asyncio
import json
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from database import engine
from models import Question
from models import Base



async def load_questions(json_files:list[str]) -> None:
    async with AsyncSessionLocal() as session:
        for file in json_files:
            with open(file, "r", encoding="utf-8") as f:
                questions = json.load(f)

            for q in questions:
                question = Question(
                    text=q["text"],
                    category=q["category"],
                    option1=q["options"][0], # The correct option
                    option2=q["options"][1],
                    option3=q["options"][2],
                    option4=q["options"][3]
                )
                session.add(question)

        await session.commit()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



if __name__ == "__main__":
    # asyncio.run(init_db())
    json_files = sys.argv[1:]
    asyncio.run(load_questions(json_files))
