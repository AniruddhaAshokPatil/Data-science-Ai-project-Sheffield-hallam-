from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Query, status


TOKEN_TTL_HOURS = int(os.getenv("SHIELDWISE_TOKEN_TTL_HOURS", "8"))
TOKEN_SECRET = os.getenv("SHIELDWISE_TOKEN_SECRET", "development-only-secret-change-me")


@dataclass
class AuthenticatedUser:
    username: str
    role: str
    full_name: str
    email: str


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    # I hash passwords with PBKDF2 here so stored credentials are not kept in plain text.
    password_salt = salt or secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt.encode("utf-8"),
        120000,
    ).hex()
    return password_salt, password_hash


def verify_password(password: str, *, salt: str, password_hash: str) -> bool:
    _, computed_hash = hash_password(password, salt=salt)
    return hmac.compare_digest(computed_hash, password_hash)


def create_access_token(*, username: str, role: str, full_name: str, email: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)
    payload = {
        "username": username,
        "role": role,
        "full_name": full_name,
        "email": email,
        "exp": expires_at.isoformat(),
    }
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    signature = hmac.new(TOKEN_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{encoded_payload}.{signature}"


def decode_access_token(token: str) -> AuthenticatedUser:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="I could not parse the access token.") from exc

    expected_signature = hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="I could not verify the access token.")

    payload = json.loads(base64.urlsafe_b64decode(encoded_payload.encode("utf-8")).decode("utf-8"))
    expires_at = datetime.fromisoformat(payload["exp"])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="I found that the access token has expired.")

    return AuthenticatedUser(
        username=payload["username"],
        role=payload["role"],
        full_name=payload["full_name"],
        email=payload["email"],
    )


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="I need an Authorization header.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="I expected a Bearer token.")
    return token


def get_current_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    token = _extract_bearer_token(authorization)
    return decode_access_token(token)


def require_user_role(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if current_user.role not in {"user", "investigator"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="I could not authorize this user role.")
    return current_user


def require_customer_role(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if current_user.role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="I need a policyholder account for claim submission.")
    return current_user


def require_investigator_role(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if current_user.role != "investigator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="I need an investigator account for this action.")
    return current_user


def get_websocket_user(token: str | None = Query(default=None)) -> AuthenticatedUser:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="I need a token query parameter.")
    return decode_access_token(token)
