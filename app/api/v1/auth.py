from fastapi import APIRouter, Depends, Response, status, Cookie
from app.core.dependencies import get_user_service
from app.core.exceptions import AuthenticationException
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin
from app.core.security import create_jwt_token, decode_jwt_token, TokenType

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.register(data)

@router.post("/login", response_model=TokenResponse)
async def user_login(data: UserLogin, response: Response, service: UserService = Depends(get_user_service)):
    user = await service.authenticate(
        email=data.email,
        password=data.password
    )

    token_payload = {
        "sub": str(user.id),
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "username": user.username,
        "is_active": user.is_active
    }
    access_token = create_jwt_token(token_payload, TokenType.ACCESS)
    refresh_token = create_jwt_token(token_payload, TokenType.REFRESH)

    response.set_cookie(
        key="refresh_token",
        value= refresh_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )

    return TokenResponse(access_token=access_token, token_type="bearer")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise AuthenticationException("Refresh token is required, please login again")

    data = decode_jwt_token(refresh_token)
    if data.get("token_type") != "refresh":
        raise AuthenticationException("Invalid refresh token")

    access_token = create_jwt_token(data, TokenType.ACCESS)

    return TokenResponse(access_token=access_token, token_type="bearer")
