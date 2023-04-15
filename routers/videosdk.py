from datetime import datetime, timedelta

import jwt, json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from firebase_admin import auth

from config import Settings
from dependencies import get_settings, oauth2_scheme

router = APIRouter(
    tags=["videosdk"],
)

video_pool = []
new_users = []
matches = []


@router.get("/get_pool")
async def get_pool():
    json_pool = []
    for el in video_pool:
        json_pool.append({
            "meeting_id": el[0],
            "user_id": el[1]
        })
    print(json_pool)

    return JSONResponse(content=json_pool, status_code=200)


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

    res_meeting_id = video_pool.pop(0)
    new_users.append([
       res_meeting_id[0], current_user["uid"]
    ])
    return JSONResponse(content={
        'meetingId': res_meeting_id[0],
        'userId': res_meeting_id[1]
    }, status_code=200)


@router.post("/find_user")
async def find_user(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    for room in new_users:
        if room[0] == req_json["mId"]:
            new_users.remove(room)
            return JSONResponse(content={
                'userId': room[1]
            }, status_code=200)
    return JSONResponse(content={
        'message': 'User not found'
    }, status_code=404)


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


# TODO: if there are 2 participants in one meeting and one of them leaves,
#  restore the mId with the other user's uId to the pool

@router.post("/delete_from_pool")
async def read_pool(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if not video_pool:
    #     req = await request.json()
    #     if req["uId"]:
    #         user_id = req["uId"]
    #         meeting_id = req["mId"]
    #
    #         video_pool.append([meeting_id, user_id])  # restoring for the user that's left
    #
    #     return JSONResponse(content='waiting', status_code=200)

    to_pop = [item for item in video_pool if item[1] == current_user["uid"]]

    for el in to_pop:
        video_pool.pop(video_pool.index(el))

    return JSONResponse(content={'status': 'deleted',
                                 'mid': to_pop[0][0],
                                 'uid': to_pop[0][1]}, status_code=200)


@router.post("/did_match")
async def read_pool(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()

    for match in matches:
        if match[0] == req_json['friendUid'] and match[1] == req_json['myUid']:
            matches.remove(match)  # resetting

        if match[1] == req_json['friendUid'] and match[0] == req_json['myUid']:
            matches.remove(match)
            return JSONResponse(content={
                'matched': 1
            }, status_code=200)

    matches.append([req_json['friendUid'], req_json['myUid']])
    return JSONResponse(content={
        'matched': 0
    }, status_code=200)
