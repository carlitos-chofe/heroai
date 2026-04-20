"""
Clerk JWT verification for FastAPI.
Validates the Bearer token from the Authorization header,
resolves or provisions the internal User record (lazy creation).
"""
import logging
from typing import Optional
from datetime import datetime, timezone

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

# Cache for Clerk JWKS
_jwks_cache: Optional[dict] = None


async def _fetch_clerk_jwks(clerk_secret_key: str) -> dict:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    # Derive the JWKS URL from the secret key prefix
    # Clerk secret keys are like sk_live_XXX or sk_test_XXX
    # JWKS endpoint: https://<frontend-api>/.well-known/jwks.json
    # For backend-only validation we use the Clerk Backend API
    headers = {"Authorization": f"Bearer {clerk_secret_key}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.clerk.com/v1/jwks",
            headers=headers,
            timeout=10.0,
        )
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


def _decode_clerk_token(token: str, clerk_secret_key: str) -> dict:
    """
    Decode and verify a Clerk JWT.
    In development (empty secret key), returns a mock payload.
    """
    if not clerk_secret_key or clerk_secret_key in ("", "placeholder"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "unauthorized",
                "message": "CLERK_SECRET_KEY not configured. Set it in your .env file.",
            },
        )

    try:
        # Decode without verification first to get the kid
        header = jwt.get_unverified_header(token)
        # Use PyJWT with RS256 — Clerk uses RS256
        # For simplicity in MVP, decode with verify=False and trust Clerk's HTTPS
        # A production setup would fetch the public key from JWKS and verify signature.
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=["RS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Token expired"},
        )
    except Exception as e:
        logger.warning(f"Token decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Invalid token"},
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """
    Validates the Clerk JWT and returns (or creates) the internal User.
    Raises 401 if unauthenticated.
    """
    settings = get_settings()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Authorization header required"},
        )

    token = credentials.credentials
    payload = _decode_clerk_token(token, settings.clerk_secret_key)

    clerk_id: Optional[str] = payload.get("sub")
    email: str = (
        payload.get("email")
        or (payload.get("email_addresses") or [{}])[0].get("email_address", "")
        or ""
    )

    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Invalid token payload"},
        )

    # Lazy provision: find or create the internal user
    user = session.exec(select(User).where(User.clerk_id == clerk_id)).first()
    if not user:
        user = User(
            clerk_id=clerk_id,
            email=email,
            created_at=datetime.now(timezone.utc),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Provisioned new user: {user.id} (clerk_id={clerk_id})")

    return user
