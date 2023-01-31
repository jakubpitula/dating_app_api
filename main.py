import uvicorn
import firebase_admin
import pyrebase
import json
import jwt
import uuid
import datetime
import os

from functools import lru_cache
from firebase_admin import credentials, auth, db
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from config import Settings

if not firebase_admin._apps:
    cred = credentials.Certificate('config/dating_app_service_account_keys.json')
    firebase = firebase_admin.initialize_app(cred, {
        'databaseURL': "https://dating-app-3e0f5-default-rtdb.europe-west1.firebasedatabase.app"
    })

pb = pyrebase.initialize_app(json.load(open('config/firebase_config.json')))
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
allow_all = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_all,
    allow_credentials=True,
    allow_methods=allow_all,
    allow_headers=allow_all
)

ref = db.reference('/')


@lru_cache()
def get_settings():
    return Settings()


@app.get("/generate_token")
async def home(settings: Settings = Depends(get_settings)):
    expires = 24 * 3600
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(seconds=expires)
    try:
        token = jwt.encode(payload={
            'apikey': settings.API_KEY,
            'permissions': ["allow_join"]
        }, key=settings.SECRET_KEY)
        return JSONResponse(content={'token': token}, status_code=200)
    except:
        return JSONResponse(content={'message': 'Error generating token'}, status_code=500)


# signup endpoint
@app.post("/signup")
async def signup(request: Request):
    req = await request.json()
    email = req['email']
    password = req['password']
    first_name = req['first_name']
    last_name = req['last_name']
    conf_pass = req['conf_pass']
    age = req['age']
    gender = req['gender']

    if not email or not password or not first_name or not last_name or not conf_pass or not age or not gender:
        return HTTPException(detail={'message': 'You have to fill in all the required fields'}, status_code=400)
    if conf_pass != password:
        return HTTPException(detail={'message': "The passwords don't match"}, status_code=400)
    if gender not in ('m', 'f', 'nb', 'pns'):
        return HTTPException(detail={'message': 'You have to choose a gender'}, status_code=400)
    try:
        user = auth.create_user(
            display_name=first_name + ' ' + last_name,
            email=email,
            password=password
        )

        users_ref = ref.child('users')
        users_ref.child(user.uid).set({
            'name': first_name + ' ' + last_name,
            'email': email,
            'age': age,
            'gender': gender
        })

        return JSONResponse(content={'uid': user.uid}, status_code=200)
    except:
        return JSONResponse(content={'message': 'Error Creating User'}, status_code=400)


# login endpoint
@app.post("/login")
async def login(request: Request):
    req_json = await request.json()
    email = req_json['email']
    password = req_json['password']
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return JSONResponse(content={'token': jwt}, status_code=200)
    except:
        return JSONResponse(content={'message': 'There was an error logging in'}, status_code=400)


@app.get("/get_user_data")  # protected route
async def get_user(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')

    try:
        auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    req_json = await request.json()
    uid = req_json['uid']
    return JSONResponse(content=ref.child("users").child(uid).get(), status_code=200)


@app.put("/user/{id}")
async def update_user(uid: str, request: Request):

    # todo:constraints on user data, update auth data

    headers = request.headers
    jwt = headers.get('authorization')

    try:
        current_user = auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    if current_user["uid"] != uid:
        return JSONResponse(content={'msg': 'Not authorized'}, status_code=401)

    req_json = await request.json()
    user = ref.child("users").child(uid)

    if "email" in req_json:
        user.update({"email": req_json["email"]})
    if "age" in req_json:
        user.update({"age": req_json["age"]})
    if "gender" in req_json:
        user.update({"gender": req_json["gender"]})
    if "name" in req_json:
        user.update({"name": req_json["name"]})

    return JSONResponse(content=user.get(), status_code=200)


@app.get("/get_current_user")  # protected route
async def get_current_user(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')

    try:
        user = auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    # return user
    return JSONResponse(content=ref.child("users").child(user["uid"]).get(), status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app")
