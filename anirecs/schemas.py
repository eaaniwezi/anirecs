from pydantic import BaseModel
from datetime import datetime
from typing import Optional
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class UserUpdate(BaseModel):
    username: str 

class UserOut(BaseModel):
    id: int 
    username: str
    created_at: datetime

    # class Config:
    #     orm_mode = True
        
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class Genre(GenreBase):
    id: int
    created_at: Optional[datetime]
    
    class Config:
        orm_mode = True

class AnimeBase(BaseModel):
    title: str
    description: str
    rating: int

class AnimeCreate(AnimeBase):
    pass

class Anime(AnimeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
 
class FavouriteBase(BaseModel):
    user_id: int
    anime_id: int

class FavouriteCreate(FavouriteBase):
    pass

class Favourite(FavouriteBase):
    class Config:
        orm_mode = True
 
class PreferenceCreate(BaseModel):
    user_id: int
    genre_id: int

class Preference(BaseModel):
    user_id: int
    genre_id: int

class GenreAnimeCreate(BaseModel):
    genre_id: int
    anime_id: int

class GenreAnime(BaseModel):
    genre_id: int
    anime_id: int
