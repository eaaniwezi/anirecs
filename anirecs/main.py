from fastapi import FastAPI
from .database import engine
from . import models
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, genre, user,anime, favourite, preference, genreAnime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
app.include_router(auth.router) 
app.include_router(user.router) 
app.include_router(genre.router) 
app.include_router(anime.router) 
app.include_router(favourite.router) 
app.include_router(preference.router) 
app.include_router(genreAnime.router) 

@app.get("/")
def root():
    return {"AniRecs": "Anime Recommendation App"}

# poetry run uvicorn anirecs.main:app --reload
# pip freeze --exclude-editable > requirements.txt
