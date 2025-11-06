from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.user_schema import UserCreate, UserSchema
from app.config import settings
from app.security import create_access_token, verify_password, get_password_hash
from app.database import db

router = APIRouter()

@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate):
    """
    Create a new user and save it to Firestore.
    """
    users_ref = db.collection("users")
    existing_user = users_ref.document(user.user_id).get()
    if existing_user.exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this ID already exists",
        )
    
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data.pop("password")
    user_data["hashed_password"] = hashed_password
    
    users_ref.document(user.user_id).set(user_data)
    
    # Return the created user data (without the password)
    return UserSchema(**user.dict())

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Log in a user and return an access token.
    """
    users_ref = db.collection("users")
    user_doc = users_ref.document(form_data.username).get()
    
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = user_doc.to_dict()

    if not verify_password(form_data.password, user.get("hashed_password", "")):
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