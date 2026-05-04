from fastapi import APIRouter, HTTPException, status

from src.api.auth import create_access_token, verify_password
from src.api.db import fetch_user
from src.api.schemas import LoginRequest, LoginResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(login_request: LoginRequest) -> LoginResponse:
    # Check the username and password, then return a token that includes the user's role.
    user_row = fetch_user(login_request.username)
    if user_row is None or int(user_row["is_active"]) != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active user account was found.")

    if not verify_password(
        login_request.password,
        salt=user_row["password_salt"],
        password_hash=user_row["password_hash"],
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The login credentials could not be verified.")

    access_token = create_access_token(
        username=user_row["username"],
        role=user_row["role"],
        full_name=user_row["full_name"],
        email=user_row["email"],
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        role=user_row["role"],
        username=user_row["username"],
        full_name=user_row["full_name"],
        email=user_row["email"],
    )
