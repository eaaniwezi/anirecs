from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from .. import database, models, schemas
from sqlalchemy.orm import Session
from .user import current_user
from typing import List
 

router = APIRouter(
    tags=['favourites']
)

@router.post("/user/addfavourites", response_model=schemas.Favourite)
async def favourite_anime(favourite: schemas.FavouriteCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == favourite.user_id).first()
        db_anime = db.query(models.Anime).filter(models.Anime.id == favourite.anime_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not db_anime:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
        db_favourite = models.Favourite(user_id=favourite.user_id, anime_id=favourite.anime_id)
        db.add(db_favourite)
        db.commit()
        db.refresh(db_favourite)
        return db_favourite
    except IntegrityError as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User id and anime id already exists")
        else:
            raise


@router.delete("/user/removefavourites/{user_id}/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfavourite_anime(user_id: int, anime_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    db_favourite = db.query(models.Favourite).filter(models.Favourite.user_id == user_id, models.Favourite.anime_id == anime_id).first()
    if not db_favourite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favourite not found")
    
    db.delete(db_favourite)
    db.commit()
    return None


@router.get("/user/favourites/{user_id}")
async def get_user_favourited_anime(user_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    favourites = db.query(models.Anime).join(models.Favourite).filter(models.Favourite.user_id == user_id).all()
    return favourites

