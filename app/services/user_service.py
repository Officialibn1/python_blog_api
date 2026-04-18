from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.db import UserDB
from app.core.exceptions import NotFoundException, ConflictException, AuthenticationException
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, user: UserCreate) -> UserDB:
        user_exists = await self.user_repo.get_by_email(email=user.email)
        if user_exists:
            raise ConflictException("Email already used.")

        hashed_password = hash_password(user.password)

        new_user = await self.user_repo.create(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )

        return new_user

    async def get_user(self, user_id: int) -> UserDB:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        return user

    async def authenticate(self, email: str, password: str) -> UserDB:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationException("Invalid credentials")

        valid_password = verify_password(raw_password=password, hashed_password=user.hashed_password)
        if not valid_password:
            raise AuthenticationException("Invalid credentials")

        return user
