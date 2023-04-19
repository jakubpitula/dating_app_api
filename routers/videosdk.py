from datetime import datetime, timedelta

import jwt, json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from firebase_admin import auth

from config import Settings
from dependencies import get_settings, oauth2_scheme
from sse_starlette.sse import EventSourceResponse
from queue import Queue

router = APIRouter(
    tags=["videosdk"],
)

video_pool = []
new_users = []
matches = []
users_queue = Queue()


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


@router.get("/get_pool")
async def get_pool():
    return JSONResponse(content=video_pool, status_code=200)


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

    res_meeting = {}
    for video in video_pool:
        if video["in_progress"] == 0:
            res_meeting = video
            video["in_progress"] = 1
    if res_meeting:
        res_meeting["answerer"] = {
            "id": current_user["uid"],
            "join_status": 1
        }
        new_users.append([
            res_meeting["mId"], current_user["uid"]
        ])
        return JSONResponse(content={
            'meetingId': res_meeting["mId"],
            'userId': res_meeting["caller"]["id"],
            "res_meeting": res_meeting
        }, status_code=200)
    else:
        return JSONResponse(content='waiting', status_code=200)


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

    new_video = {"mId": req_json["mId"], "caller": {
        "id": current_user["uid"],
        "join_status": 1
    }, "answerer": {
        "id": "",
        "join_status": 0
    },
                 "in_progress": 0}
    video_pool.append(new_video)

    return JSONResponse(content={'status': 'added'}, status_code=200)


@router.post("/get_remote_join_status")
async def get_remote_join_status(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    for video in video_pool:
        if video["mId"] == req_json["mId"]:
            if video["caller"]["id"] == current_user["uid"]:
                return JSONResponse(content={'status': video["answerer"]["join_status"],
                                             'content': video_pool}, status_code=200)
            else:
                return JSONResponse(content={'status': video["caller"]["join_status"],
                                             'content': video_pool}, status_code=200)

    return JSONResponse(content={'status': -1, 'content': video_pool}, status_code=404)


@router.post("/mark_joined")
async def mark_joined(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    meeting_id = req_json["mId"]

    for video in video_pool:
        if video["mId"] == meeting_id:
            if video["caller"]["id"] == current_user["uid"]:
                video["caller"]["join_status"] = 2
            elif video["answerer"]["id"] == current_user["uid"]:
                video["answerer"]["join_status"] = 2

    return JSONResponse(content=video_pool, status_code=200)


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

    to_pop = [video for video in video_pool if
              current_user["uid"] in
              (video["caller"]["id"], video["answerer"]["id"])]

    for el in to_pop:
        video_pool.pop(video_pool.index(el))

    return JSONResponse(content={'status': 'deleted',
                                 'popped': to_pop}, status_code=200)


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


@router.get("/delete_pool")
async def delete_pool():
    video_pool.clear()

    return JSONResponse(content=video_pool, status_code=200)


ready_meetings = []


@router.post("/add_user_to_queue")
async def add_user_to_queue(token: str = Depends(oauth2_scheme)):
    beg = users_queue.qsize()
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if current_user["uid"] not in users_queue:
    #     users_queue.append(current_user["uid"])
    users_queue.put(current_user["uid"])

    if users_queue.qsize() >= 2:
        user1 = users_queue.get()
        user2 = users_queue.get()

        user_to_return = user1
        if current_user["uid"] == user1:
            user_to_return = user2
        return JSONResponse(content={'status': 'matched', 'uid': user_to_return}, status_code=200)

    return JSONResponse(content={'status': 'added', 'queue size': users_queue.qsize(),
                                 'queue size beg ': beg}, status_code=200)

    # users_queue[0] to be replaced with a matching algorithm
    # users to be added to queue always, then match with others


@router.post("/add_match")
async def add_match(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    ready_meetings.append({
        'uid1': current_user["uid"],
        'uid2': req_json["matchId"],
        'mId': req_json["mId"]
    })

    return JSONResponse(content=ready_meetings, status_code=200)


@router.get("/matched_event")
async def message_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if ready_meetings:
                yield {
                    "event": "match",
                    "data": ready_meetings,
                }
            # else:
            #     yield {
            #         "event": "end_event",
            #         "data": "End of the stream",
            #     }

    return EventSourceResponse(event_generator())
