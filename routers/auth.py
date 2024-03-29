from fastapi import APIRouter, HTTPException
from fastapi import Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin import auth, storage
from fastapi.responses import JSONResponse

from models import Token
from dependencies import pb, ref
from datetime import date, datetime

router = APIRouter(
    tags=["auth"],
)


# signup endpoint
@router.post("/signup")
async def signup(request: Request):
    req = await request.json()

    if 'email' not in req.keys() or 'password' not in req.keys() or 'first_name' not in req.keys() or \
            'last_name' not in req.keys() or 'conf_pass' not in req.keys() or 'date' not in req.keys() or \
            'gender' not in req.keys() or 'profilePicUrl' not in req.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You have to fill in all the required fields'
        )

    email = req['email']
    password = req['password']
    first_name = req['first_name']
    last_name = req['last_name']
    conf_pass = req['conf_pass']
    birthdate = req['date']
    gender = req['gender']
    profile_pic_url = req['profilePicUrl']

    if conf_pass != password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The passwords don't match"
        )
    if gender not in ('m', 'f'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You have to choose a valid gender'
        )
    #
    today = date.today()
    birth = datetime.strptime(birthdate, "%d/%m/%Y")
    print(birth)
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    if int(age) < 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You have to be 18 or older'
        )

    try:
        user = auth.create_user(
            display_name=first_name + ' ' + last_name,
            email=email,
            password=password,
            photo_url=profile_pic_url,
        )

        users_ref = ref.child('users')
        users_ref.child(user.uid).set({
            'name': first_name + ' ' + last_name,
            'email': email,
            'birthdate': birthdate,
            'gender': gender,
            'profilePicUrl': profile_pic_url
        })

        return JSONResponse(content={'uid': user.uid}, status_code=200)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error creating user'
        )


# login endpoint
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = pb.auth().sign_in_with_email_and_password(form_data.username, form_data.password)
        access_token = user['idToken']
        return {"access_token": access_token, "token_type": "bearer"}
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
