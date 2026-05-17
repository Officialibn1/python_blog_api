from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException
from app.models.db import UserDB

class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        email: str,
        username: str,
        hashed_password: str
    ) -> UserDB:
        """Creating and storing a new user in the database"""

        db_user = UserDB(
            email=email,
            username=username,
            hashed_password=hashed_password
        )

        self.db.add(db_user)
        await self.db.flush()
        await self.db.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: int) -> UserDB | None:
        """Fetching a single user from the database using the id"""
        query = select(UserDB).where(UserDB.id == user_id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserDB | None:
        """Fetching a single user from the database using the email"""
        query = select(UserDB).where(UserDB.email == email)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> UserDB | None:
        """Fetch a single user form the database using the username"""
        query = select(UserDB).where(UserDB.username == username)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()


    async def get_all(self, skip: int, limit: int) -> tuple[list[UserDB], int]:
        """Fetching all users on the database using page and limit for pagination"""
        query = select(UserDB)
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()
        result = await self.db.execute(query.offset(skip).limit(limit))

        return list(result.scalars().all()), total

    async def update(self, user_id: int, **fields) -> UserDB:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        for key, value in fields.items():
            setattr(user, key, value)

        user.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def activate_or_deactivate_user(self, user_id: int) -> UserDB:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        setattr(user, "is_active", False if user.is_active else True)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update_password(self, user_id: int, hashed_password: str) -> None:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        user.hashed_password = hashed_password
        await self.db.flush()

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        await self.db.delete(user)
