import uvicorn
import firebase_admin
import pyrebase
import json

from firebase_admin import credentials, auth
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

if not firebase_admin._apps:
    cred = credentials.Certificate('config/dating_app_service_account_keys.json')
    firebase = firebase_admin.initialize_app(cred)
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


# signup endpoint
@app.post("/signup")
async def signup(request: Request):
    req = await request.json()
    email = req['email']
    password = req['password']
    first_name = req['first_name']
    last_name = req['last_name']
    conf_pass = req['conf_pass']
    if not email or not password or not first_name or not last_name or not conf_pass:
        return HTTPException(detail={'message': 'You have to fill in all the required fields'}, status_code=400)
    if conf_pass != password:
        return HTTPException(detail={'message': "The passwords don't match"}, status_code=400)
    try:
        user = auth.create_user(
            display_name=first_name + ' ' + last_name,
            email=email,
            password=password
        )
        return JSONResponse(content={'uid': user.uid}, status_code=200)
    except:
        return HTTPException(detail={'message': 'Error Creating User'}, status_code=400)


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
        return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)


@app.get("/get_user_data") #protected route
async def get_users(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')

    try:
        auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    req_json = await request.json()
    uid = req_json['uid']
    requested_user = auth.get_user(uid)
    return JSONResponse(content={
        'name': requested_user.display_name,
        'email': requested_user.email
    }, status_code=200)


@app.get("/get_current_user") #protected route
async def get_users(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')

    try:
        user = auth.verify_id_token(jwt)
    except:
        return JSONResponse(content={'msg': 'Not authenticated'}, status_code=401)

    # return user
    return JSONResponse(content={
        'name': user["name"],
        'email': user["email"]
    }, status_code=200)



if __name__ == "__main__":
    uvicorn.run("main:app")
