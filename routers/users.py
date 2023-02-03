from fastapi import APIRouter, Depends, Request
from firebase_admin import credentials, auth, db
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
ref = db.reference('/')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/users/{uid}")  # protected route
async def get_user(uid: str, request: Request):
    headers = request.headers
    jwt = headers.get('authorization')

    try:
        auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    return JSONResponse(content=ref.child("users").child(uid).get(), status_code=200)


@router.put("/user/{uid}")
async def update_user(uid: str, request: Request):
    # todo:constraints on user data

    headers = request.headers
    jwt = headers.get('authorization')

    try:
        current_user = auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    if current_user["uid"] != uid:
        return JSONResponse(content={'msg': 'Not authorized'}, status_code=401)

    req_json = await request.json()
    try:
        auth.update_user(
            uid,
            email=req_json["email"] if "email" in req_json else auth.get_user(uid).email,
            display_name=req_json["name"] if "name" in req_json else auth.get_user(uid).display_name
        )
    except:
        return JSONResponse(content={'msg': 'Incorrect data'}, status_code=400)

    user = ref.child("users").child(uid)

    try:
        if "email" in req_json:
            user.update({"email": req_json["email"]})
        if "age" in req_json:
            user.update({"age": req_json["age"]})
        if "gender" in req_json and req_json["gender"] in ('m', 'f', 'nb', 'pns'):
            user.update({"gender": req_json["gender"]})
        if "name" in req_json:
            user.update({"name": req_json["name"]})
    except:
        return JSONResponse(content={"msg": "Error updating user"}, status_code=500)

    return JSONResponse(content=user.get(), status_code=200)


@router.get("/users/me")  # protected route
async def get_user_me(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')

    try:
        user = auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    # return user
    return JSONResponse(content=ref.child("users").child(user["uid"]).get(), status_code=200)