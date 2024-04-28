from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import schemas, models, database
from .user import current_user
from typing import List

router = APIRouter(
    tags=['preferences']
)

@router.post("/user/addpreferences", response_model=schemas.Preference)
async def add_preference(preference: schemas.PreferenceCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == preference.user_id).first()
        db_genre = db.query(models.Genre).filter(models.Genre.id == preference.genre_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not db_genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
        db_preference = models.Preference(user_id=preference.user_id, genre_id=preference.genre_id)
        db.add(db_preference)
        db.commit()
        db.refresh(db_preference)
        return db_preference
    except IntegrityError as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Entry with the same user id and genre id already exists")
        else:
            raise

@router.delete("/user/removepreferences/{user_id}/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_preference(user_id: int, genre_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")

    db_preference = db.query(models.Preference).filter(models.Preference.user_id == user_id, models.Preference.genre_id == genre_id).first()
    if not db_preference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")
    
    db.delete(db_preference)
    db.commit()
    return None

@router.get("/preferences/{user_id}", response_model=List[schemas.Genre])
async def get_user_preferences(user_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    preferences = db.query(models.Genre).join(models.Preference).filter(models.Preference.user_id == user_id).all()
    return preferences


