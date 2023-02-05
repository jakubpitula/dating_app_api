import json
import uvicorn
import firebase_admin
import pyrebase

from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import users, auth, videosdk

if not firebase_admin._apps:
    cred = credentials.Certificate('config/dating_app_service_account_keys.json')
    firebase = firebase_admin.initialize_app(cred, {
        'databaseURL': "https://dating-app-3e0f5-default-rtdb.europe-west1.firebasedatabase.app"
    })

pb = pyrebase.initialize_app(json.load(open('config/firebase_config.json')))

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(videosdk.router)

allow_all = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_all,
    allow_credentials=True,
    allow_methods=allow_all,
    allow_headers=allow_all
)

if __name__ == "__main__":
    uvicorn.run("main:app")
