from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseUser(BaseModel):
    name: str
    age: int
    gender: str


class CurrentUser(BaseUser):
    email: str