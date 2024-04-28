from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from .. import schemas, database, models
from sqlalchemy.orm import Session
from .user import current_user
from typing import List

router = APIRouter(
    tags=['genre_anime']
)

@router.post("/genre-anime", status_code=status.HTTP_201_CREATED, response_model=schemas.GenreAnime)
async def create_genre_anime(genre_anime: schemas.GenreAnimeCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    try:
        db_genre = db.query(models.Genre).filter(models.Genre.id == genre_anime.genre_id).first()
        db_anime = db.query(models.Anime).filter(models.Anime.id == genre_anime.anime_id).first()
        if not db_genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
        if not db_anime:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
        db_genre_anime = models.GenreAnime(genre_id=genre_anime.genre_id, anime_id=genre_anime.anime_id)
        db.add(db_genre_anime)
        db.commit()
        db.refresh(db_genre_anime)
        return db_genre_anime
    except IntegrityError as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Entry with the same anime id and genre id already exists")
        else:
            raise

@router.get("/genre-anime", response_model=List[schemas.GenreAnime])
async def get_all_genre_anime(current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    genre_anime = db.query(models.GenreAnime).all()
    return genre_anime

@router.get("/genre-anime/genre/{genre_id}")
async def get_genre_anime_from_genre_id(genre_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre_animes = db.query(models.Anime).join(models.GenreAnime).filter(models.GenreAnime.genre_id == genre_id).all()
    if not db_genre_animes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre-anime associations not found for the given genre ID")
    return db_genre_animes

@router.get("/genre-anime/anime/{anime_id}")
async def get_genre_anime_from_anime_id(anime_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre_animes = db.query(models.Genre).join(models.GenreAnime).filter(models.GenreAnime.anime_id == anime_id).all()
    if not db_genre_animes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre-anime associations not found for the given anime ID")
    return db_genre_animes

@router.delete("/genre-anime/{genre_id}/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre_anime(genre_id: int, anime_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre_anime = db.query(models.GenreAnime).filter(models.GenreAnime.genre_id == genre_id, models.GenreAnime.anime_id == anime_id).first()
    if not db_genre_anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre-anime association not found")
    db.delete(db_genre_anime)
    db.commit()
    return None

@router.delete("/genre-anime/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre_anime_by_genre_id(genre_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre_animes = db.query(models.GenreAnime).filter(models.GenreAnime.genre_id == genre_id).all()
    if not db_genre_animes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre-anime associations not found for the given genre ID")
    for db_genre_anime in db_genre_animes:
        db.delete(db_genre_anime)
    db.commit()
    return None

@router.delete("/genre-anime/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre_anime_by_anime_id(anime_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_genre_animes = db.query(models.GenreAnime).filter(models.GenreAnime.anime_id == anime_id).all()
    if not db_genre_animes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre-anime associations not found for the given anime ID")
    for db_genre_anime in db_genre_animes:
        db.delete(db_genre_anime)
    db.commit()
    return None



