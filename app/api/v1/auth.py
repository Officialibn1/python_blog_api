from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Response, status, Cookie
from app.core.dependencies import get_current_user, get_user_service
from app.core.exceptions import AuthenticationException
from app.services.user_service import UserService
from app.schemas.user import LogoutResponse, UserCreate, UserResponse, TokenResponse, UserLogin
from app.core.security import create_jwt_token, decode_jwt_token, TokenType
from app.core.limiter import limiter
from app.core.cache import blacklist_token, is_token_blacklisted

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(limit_value='10/minute', per_method=True, error_message="Your browser is making requests at abnormal rates")
async def register_user(
    request: Request,
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.register(data)

@router.post("/login", response_model=TokenResponse)
@limiter.limit(limit_value='10/minute', per_method=True, error_message="Your browser is making requests at abnormal rates")
async def user_login(
    request: Request,
    data: UserLogin,
    response: Response,
    service: UserService = Depends(get_user_service)
):
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
@limiter.limit(limit_value='10/minute', per_method=True, error_message="Your browser is making requests at abnormal rates")
async def refresh_access_token(
    request: Request,
    refresh_token: str | None = Cookie(default=None)
):
    if not refresh_token:
        raise AuthenticationException("Refresh token is required, please login again")

    data = decode_jwt_token(refresh_token)
    if data.get("token_type") != "refresh":
        raise AuthenticationException("Invalid refresh token")

    jti = data.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise AuthenticationException("Refresh token has been revoked, please authenticate again")

    access_token = create_jwt_token(data, TokenType.ACCESS)

    return TokenResponse(access_token=access_token, token_type="bearer")

@router.post("/logout", response_model=LogoutResponse)
@limiter.limit(limit_value="10/minute", per_method=True, error_message="Too many requests")
async def logout(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
    refresh_token: str | None = Cookie(default=None)
):
    jti = current_user.get("jti")
    exp = current_user.get("exp")
    if jti and exp:
        ttl = exp - int(datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            await blacklist_token(jti, ttl)

    if refresh_token:
        data = decode_jwt_token(refresh_token)
        jti = data.get("jti")
        exp = data.get("exp")
        if jti and exp:
            ttl = exp - int(datetime.now(timezone.utc).timestamp())
            if ttl > 0:
                await blacklist_token(jti, ttl)
                response.delete_cookie("refresh_token")

    return {
        "success": True,
        "message": "Logged out successfully"
    }
