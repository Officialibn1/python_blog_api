from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, AdminUpdateUser, UserUpdateUser
from app.models.db import UserDB
from app.core.exceptions import NotFoundException, ConflictException, AuthenticationException
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, user: UserCreate) -> UserDB:
        user_exists = await self.user_repo.get_by_email(email=user.email)
        if user_exists:
            raise ConflictException("Email already used!")

        username_exists = await self.user_repo.get_by_username(username=user.username)
        if username_exists:
            raise ConflictException("Username already taken!")

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

    async def get_users(self, page: int = 1, size: int = 10) -> tuple[list[UserDB], int]:
        skip = (page - 1) * size
        users, total = await self.user_repo.get_all(skip=skip, limit=size)
        return users, total

    async def update_user(self, user_id: int, data: AdminUpdateUser | UserUpdateUser) -> UserDB:
        user_dict = data.model_dump()
        return await self.user_repo.update(user_id, **user_dict)

    async def authenticate(self, email: str, password: str) -> UserDB:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationException("Invalid credentials")

        if not user.is_active:
            raise AuthenticationException("Account is disabled")

        valid_password = verify_password(raw_password=password, hashed_password=user.hashed_password)
        if not valid_password:
            raise AuthenticationException("Invalid credentials")

        return user

    async def toggle_user_active_status(self, user_id: int):
        return await self.user_repo.activate_or_deactivate_user(user_id)
