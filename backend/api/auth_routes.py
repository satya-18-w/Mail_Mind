"""Google OAuth2 authentication routes."""

import datetime
import urllib.parse

import httpx
import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.database.session import get_db
from backend.database.models import User
from backend.api.dependencies import get_current_user
from backend.api.schemas import UserOut, TokenResponse

router = APIRouter(tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

SCOPES = " ".join([
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
])


def create_access_token(user_id: int) -> str:
    """Create a JWT access token for a user."""
    settings = get_settings()
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.jwt_expiry_days),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return pyjwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


@router.get("/auth/google/login")
async def google_login():
    """Redirect the user to Google's OAuth2 consent screen."""
    settings = get_settings()
    params = {
        "client_id": settings.gmail_client_id,
        "redirect_uri": settings.gmail_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/auth/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth2 callback - exchange code for tokens, create/update user."""
    settings = get_settings()

    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.gmail_redirect_uri,
            },
        )
        if token_response.status_code != 200:
            return RedirectResponse(
                f"{settings.frontend_url}/login?error=token_exchange_failed"
            )
        tokens = token_response.json()

    # Get user info from Google
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if user_response.status_code != 200:
            return RedirectResponse(
                f"{settings.frontend_url}/login?error=userinfo_failed"
            )
        user_info = user_response.json()

    # Upsert user in database
    result = await db.execute(
        select(User).where(User.google_id == user_info["id"])
    )
    user = result.scalar_one_or_none()

    if user:
        user.name = user_info.get("name", user.name)
        user.picture = user_info.get("picture", user.picture)
        user.gmail_access_token = tokens.get("access_token")
        if tokens.get("refresh_token"):
            user.gmail_refresh_token = tokens["refresh_token"]
        user.gmail_token_expiry = str(tokens.get("expires_in", ""))
    else:
        user = User(
            google_id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture"),
            gmail_access_token=tokens.get("access_token"),
            gmail_refresh_token=tokens.get("refresh_token"),
            gmail_token_expiry=str(tokens.get("expires_in", "")),
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    # Create JWT
    access_token = create_access_token(user.id)

    # Redirect to frontend with token
    return RedirectResponse(
        f"{settings.frontend_url}?token={access_token}"
    )


@router.get("/auth/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    """Get the currently authenticated user."""
    return user
