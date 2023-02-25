from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from firebase_admin import auth

from config import Settings
from dependencies import get_settings, oauth2_scheme

router = APIRouter(
    tags=["videosdk"],
)

video_pool = []


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


@router.post("/read_pool")
async def read_pool(token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not video_pool:
        return JSONResponse(content='waiting', status_code=200)

    res_meeting_id = video_pool[0]
    video_pool.pop(0)
    return JSONResponse(content={
        'meetingId': res_meeting_id[0],
        'userId': res_meeting_id[1]
    }, status_code=200)


@router.post("/add_pool")
async def add_pool(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()

    video_pool.append([req_json["mId"], current_user["uid"]])
    return JSONResponse(content={'status': 'added'}, status_code=200)
