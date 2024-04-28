from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from ..database import get_db, SessionLocal
from .. import models, schemas, utils, oauth2, database
from fastapi import Response, status, HTTPException, Depends, APIRouter

router = APIRouter(
    tags=['auth']
)

oauth2_scheme = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    hashed_password = utils.hash(user.password)
    new_user = models.User(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post('/login')
async def login(user_credentials: schemas.UserLogin = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.username == user_credentials.username).first()
    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(database.get_db)):
    try:
        payload = oauth2.verify_token(refresh_token, credentials_exception=HTTPException(status_code=401, detail="Invalid token or expired token"))
        user_id = payload.get("user_id")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_access_token = oauth2.create_access_token(data={"user_id": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        check = oauth2.verify_token(token.credentials, credentials_exception=HTTPException(status_code=401, detail="Invalid token or expired token"))
        print(f"Checks:{check}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Successfully logged out"}


