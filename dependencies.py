from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth, db

from config import Settings
import pyrebase
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pb = pyrebase.initialize_app(json.load(open('config/firebase_config.json')))
ref = db.reference('/')

@lru_cache()
def get_settings():
    return Settings()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        userid = auth.verify_id_token(token)
        if userid is None:
            raise credentials_exception
    except:
        raise credentials_exception

    user = ref.child("users").child(userid["uid"]).get()
    return user
