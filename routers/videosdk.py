from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from config import Settings
from dependencies import get_settings

router = APIRouter(
    tags=["videosdk"],
)


@router.get("/generate_token")
async def home(settings: Settings = Depends(get_settings)):
    expires_delta = 24 * 3600
    now = datetime.utcnow()
    expire = now + timedelta(seconds=expires_delta)

    token = jwt.encode(payload={
        'apikey': settings.API_KEY,
        'permissions': ["allow_join"],
        'exp': expire
    }, key=settings.SECRET_KEY)

    return JSONResponse(content={'token': token}, status_code=200)
