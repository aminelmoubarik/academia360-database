from fastapi import APIRouter, HTTPException, Depends

from auth import (
    verify_password,
    create_access_token,
    get_user_by_email,
    get_current_user
)
from models import LoginRequest


router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(credentials: LoginRequest):
    user = get_user_by_email(credentials.email)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user["password_hash"] is None:
        raise HTTPException(status_code=401, detail="User password is not configured")

    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={
            "sub": user["email"],
            "role": user["role"]
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        }
    }


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"]
    }