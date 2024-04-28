from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database, models
from .user import current_user

router = APIRouter(tags=['animes'])

@router.post("/animes", status_code=status.HTTP_201_CREATED, response_model=schemas.Anime)
async def create_anime(anime: schemas.AnimeCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_anime = models.Anime(title=anime.title, description=anime.description, rating=anime.rating)
    db.add(db_anime)
    db.commit()
    db.refresh(db_anime)
    return db_anime

@router.get("/animes", response_model=list[schemas.Anime])
async def get_all_animes(search: str = None, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    if search:
        animes = db.query(models.Anime).filter(models.Anime.title.ilike(f"%{search}%")).all()
    else:
        animes = db.query(models.Anime).all()
    return animes

@router.get("/animes/{anime_id}", response_model=schemas.Anime)
async def get_anime(anime_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
    return db_anime

@router.put("/animes/{anime_id}", response_model=schemas.Anime)
async def update_anime(anime_id: int, anime: schemas.AnimeCreate, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
    db_anime.title = anime.title
    db_anime.description = anime.description
    db_anime.rating = anime.rating
    db.commit()
    db.refresh(db_anime)
    return db_anime

@router.delete("/animes/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_anime(anime_id: int, current_user: schemas.UserOut = Depends(current_user), db: Session = Depends(database.get_db)):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
    db.delete(db_anime)
    db.commit()
    return None
