"""
CRUD opprations and business logic
"""


async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    A(bs=[B(data="b1"), B(data="b2")], data="a1"),
                    A(bs=[], data="a2"),
                    A(bs=[B(data="b3"), B(data="b4")], data="a3"),
                ]
            )
