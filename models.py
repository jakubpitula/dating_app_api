from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseUser(BaseModel):
    name: str
    age: int
    gender: str
    profilePicUrl: str | None = None


class CurrentUser(BaseUser):
    email: str
