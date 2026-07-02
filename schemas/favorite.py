from pydantic import BaseModel


class FavoriteRequest(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")