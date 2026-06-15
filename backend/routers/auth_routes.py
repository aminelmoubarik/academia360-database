"""Authentication routes with brute-force protection.

Login attempts are rate-limited per client IP using a sliding window:
more than MAX_ATTEMPTS failures within WINDOW_SECONDS returns HTTP 429.
Successful logins reset the counter. This blocks credential-stuffing
and dictionary attacks without any external dependency.
"""
import logging
import time
from collections import defaultdict
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from models import TokenResponse

logger = logging.getLogger("academia360.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- sliding-window rate limiter (in-memory, per worker) ---
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
_failed_attempts: dict[str, list[float]] = defaultdict(list)


def _is_rate_limited(client_ip: str) -> bool:
    now = time.monotonic()
    window = _failed_attempts[client_ip]
    # drop attempts older than the window
    _failed_attempts[client_ip] = [t for t in window if now - t < WINDOW_SECONDS]
    return len(_failed_attempts[client_ip]) >= MAX_ATTEMPTS


def _register_failure(client_ip: str) -> None:
    _failed_attempts[client_ip].append(time.monotonic())


def _reset(client_ip: str) -> None:
    _failed_attempts.pop(client_ip, None)


@router.post("/login", response_model=TokenResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning("Rate limit hit for %s", client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again in a minute.",
            headers={"Retry-After": str(WINDOW_SECONDS)},
        )

    user = authenticate_user(email=form_data.username, password=form_data.password)

    if user is None:
        _register_failure(client_ip)
        logger.info("Failed login for %s from %s", form_data.username, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _reset(client_ip)
    logger.info("Login OK: %s (%s)", user["email"], user["role"])

    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
