from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from .. import schemas, database, models
from sqlalchemy.orm import Session
from .user import current_user
from fastapi import Query

router = APIRouter(
    tags=['genres']
)

@router.post("/genres", status_code=status.HTTP_201_CREATED, response_model=schemas.Genre)
async def create_genre(genre: schemas.GenreCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    existing_genre = db.query(models.Genre).filter(models.Genre.name == genre.name).first()
    if existing_genre:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Genre name already exists")
    db_genre = models.Genre(name=genre.name)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

@router.get("/genres", response_model=list[schemas.Genre])
async def get_all_genres(search: str = None, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    if search:
        genres = db.query(models.Genre).filter(models.Genre.name.ilike(f"%{search}%")).all()
    else:
        genres = db.query(models.Genre).all()
    return genres

@router.get("/genres/{genre_id}", response_model=schemas.Genre)
async def get_genre(genre_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return db_genre

@router.put("/genres/{genre_id}", response_model=schemas.Genre)
async def update_genre(genre_id: int, genre: schemas.GenreCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    db_genre.name = genre.name
    db.commit()
    db.refresh(db_genre)
    return db_genre

@router.delete("/genres/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    db.delete(db_genre)
    db.commit()
    return None
