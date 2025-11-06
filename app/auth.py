from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.user_schema import UserCreate, UserSchema
from app.config import settings
from app.security import create_access_token, verify_password, get_password_hash

router = APIRouter()

# In-memory user database (for demonstration purposes)
# In a real application, use a proper database
fake_users_db = {}

@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate):
    """
    Create a new user.
    """
    if user.user_id in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this ID already exists",
        )
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data.pop("password")
    fake_users_db[user.user_id] = {**user_data, "hashed_password": hashed_password}
    return UserSchema(**user_data)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Log in a user and return an access token.
    """
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
