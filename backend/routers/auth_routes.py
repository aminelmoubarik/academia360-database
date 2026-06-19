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
from db import get_connection
from services.audit_logger import log_audit

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


def _write_login_audit(user: dict | None, *, action: str, email: str, client_ip: str, user_agent: str | None, summary: str):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        current_user = None
        if user is not None:
            current_user = {
                "user_id": user.get("user_id"),
                "email": user.get("email"),
                "role": user.get("role"),
            }
        log_audit(
            cursor,
            current_user=current_user,
            action=action,
            module="authentication",
            entity_type="session",
            entity_id=email,
            summary=summary,
            details={"email": email},
            ip_address=client_ip,
            user_agent=user_agent,
        )
        connection.commit()
    except Exception as exc:  # noqa: BLE001 - login must not depend on audit table
        logger.warning("Login audit skipped: %s", exc)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


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
        _write_login_audit(
            None,
            action="login_failed",
            email=form_data.username,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent"),
            summary=f"Tentativa de login falhada: {form_data.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _reset(client_ip)
    logger.info("Login OK: %s (%s)", user["email"], user["role"])
    _write_login_audit(
        user,
        action="login_success",
        email=user["email"],
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent"),
        summary=f"Login efetuado: {user['email']}",
    )

    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
