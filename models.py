from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseUser(BaseModel):
    name: str | None = None
    age: int | None = None
    gender: str | None = None


class CurrentUser(BaseUser):
    email: str | None = None