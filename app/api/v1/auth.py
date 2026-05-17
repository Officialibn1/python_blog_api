import json
import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Response, status, Cookie
from app.core.dependencies import get_current_user, get_user_service
from app.core.exceptions import AuthenticationException, NotFoundException
from app.services.user_service import UserService
from app.schemas.user import LogoutResponse, UserCreate, UserResponse, TokenResponse, UserLogin, ForgotPassword, ForgotPasswordResponse, ResetPassword, ResetPasswordResponse
from app.core.security import create_jwt_token, decode_jwt_token, TokenType
from app.core.limiter import limiter
from app.core.cache import blacklist_token, cache_delete, is_token_blacklisted, set_reset_token, get_reset_email
from app.core.email import send_reset_password_email

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

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit(limit_value="5/minute", per_method=True, error_message="Too many requests")
async def forgot_password(
    request: Request,
    data: ForgotPassword,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.get_user_by_email(email=data.email)
        ttl = 600
        token = secrets.token_urlsafe(32)
        print("User Email: ", user.email)
        await set_reset_token(token, email=user.email, ttl=ttl)
        await send_reset_password_email(to=user.email, token=token)
    except NotFoundException:
        pass

    return {
        "success": True,
        "message": "You'll receive an email with the reset password link if this email exists in our system"
    }

@router.post("/reset-password", response_model=ResetPasswordResponse)
@limiter.limit(limit_value="5/minute", per_method=True, error_message="Too many requests")
async def reset_password(
    request: Request,
    data: ResetPassword,
    service: UserService = Depends(get_user_service)
):
    email = await get_reset_email(data.token)
    if not email:
        raise AuthenticationException("Invalid or expired token")

    print("=" * 80)
    print("Email: ", email)
    print(type(email))

    try:
        user = await service.get_user_by_email(email)
        await service.update_user_password(user_id=user.id, new_password=data.new_password)
    except NotFoundException:
        raise AuthenticationException("Invalid or expired token")

    await cache_delete(f"reset_token:{data.token}")
    return {
        "success": True,
        "message": "Your password have been successfully changed."
    }
