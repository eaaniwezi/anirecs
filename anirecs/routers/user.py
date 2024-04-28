from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from ..database import get_db, SessionLocal
from .. import models, schemas, utils, oauth2, database
from fastapi import Response, status, HTTPException, Depends, APIRouter

router = APIRouter(
    tags=['users']
)
oauth2_scheme = HTTPBearer()

@router.get("/users/me", tags=["users"], response_model=schemas.UserOut)
async def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    token = token.credentials
    try:
        payload = oauth2.verify_token(token, credentials_exception=HTTPException(status_code=401, detail="Invalid token or expired token"))
        userId = payload.get("user_id")
        user = db.query(models.User).filter(models.User.id == userId).first()
       
        if not user:
                raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")


@router.get("/users", response_model=list[schemas.UserOut])
async def get_users(username: str = None, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    if username:
        users = db.query(models.User).filter(models.User.username.ilike(f"%{username}%")).all()
    else:
        users = db.query(models.User).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.UserOut)
async def get_user_by_id(user_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=schemas.UserOut)
async def update_user(user_id: int, user: schemas.UserUpdate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this user")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username 
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
