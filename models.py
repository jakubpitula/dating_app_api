import datetime

from pydantic import BaseModel
from typing import Union, List


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseUser(BaseModel):
    name: str
    birthdate: str
    gender: str
    profilePicUrl: Union[str, None]


class CurrentUser(BaseUser):
    email: str
