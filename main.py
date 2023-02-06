import uvicorn
import firebase_admin

from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if not firebase_admin._apps:
    cred = credentials.Certificate('config/dating_app_service_account_keys.json')
    firebase = firebase_admin.initialize_app(cred, {
        'databaseURL': "https://dating-app-3e0f5-default-rtdb.europe-west1.firebasedatabase.app"
    })

app = FastAPI()

from routers import users, auth, videosdk

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
