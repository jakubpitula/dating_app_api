from pydantic import BaseModel
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseUser(BaseModel):
    name: str
    age: int
    gender: str
    profilePicUrl: Union[str, None]


class CurrentUser(BaseUser):
    email: str
