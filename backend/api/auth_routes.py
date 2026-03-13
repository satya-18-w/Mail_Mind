"""Google OAuth2 authentication routes."""

import datetime
import urllib.parse

import httpx
import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Request
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


def _is_local_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.hostname in {"localhost", "127.0.0.1"}
    except Exception:
        return False


def _public_origin(request: Request) -> str:
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",")[0].strip()
    forwarded_host = request.headers.get("x-forwarded-host", "").split(",")[0].strip()
    host = forwarded_host or request.headers.get("host") or request.url.netloc
    proto = forwarded_proto or request.url.scheme
    return f"{proto}://{host}"


def _extract_frontend_origin(request: Request) -> str | None:
    origin = request.headers.get("origin")
    if origin:
        return origin.rstrip("/")

    referer = request.headers.get("referer")
    if not referer:
        return None

    parsed = urllib.parse.urlparse(referer)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _resolve_google_redirect_uri(settings, request: Request) -> str:
    configured = (settings.gmail_redirect_uri or "").strip()
    if configured and not _is_local_url(configured):
        return configured
    return f"{_public_origin(request)}/auth/callback"


def _resolve_frontend_redirect_url(settings, request: Request, state: str | None) -> str:
    if state:
        parsed_state = urllib.parse.parse_qs(state)
        frontend_values = parsed_state.get("frontend", [])
        if frontend_values:
            frontend = frontend_values[0].rstrip("/")
            if frontend.startswith("http://") or frontend.startswith("https://"):
                return frontend

    configured = (settings.frontend_url or "").strip()
    if configured and not _is_local_url(configured):
        return configured.rstrip("/")

    frontend_from_request = _extract_frontend_origin(request)
    if frontend_from_request and not _is_local_url(frontend_from_request):
        return frontend_from_request

    return _public_origin(request)


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
async def google_login(request: Request, frontend: str | None = None):
    """Redirect the user to Google's OAuth2 consent screen."""
    settings = get_settings()
    redirect_uri = _resolve_google_redirect_uri(settings, request)
    frontend_origin = frontend or _extract_frontend_origin(request)
    if frontend_origin and not (frontend_origin.startswith("http://") or frontend_origin.startswith("https://")):
        frontend_origin = None
    state = urllib.parse.urlencode({"frontend": frontend_origin}) if frontend_origin else None

    params = {
        "client_id": settings.gmail_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state

    url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/auth/callback")
async def google_callback(code: str, request: Request, state: str | None = None, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth2 callback - exchange code for tokens, create/update user."""
    settings = get_settings()
    redirect_uri = _resolve_google_redirect_uri(settings, request)
    frontend_redirect = _resolve_frontend_redirect_url(settings, request, state)

    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        if token_response.status_code != 200:
            return RedirectResponse(
                f"{frontend_redirect}/login?error=token_exchange_failed"
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
                f"{frontend_redirect}/login?error=userinfo_failed"
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
        f"{frontend_redirect}?token={access_token}"
    )


@router.get("/auth/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    """Get the currently authenticated user."""
    return user
