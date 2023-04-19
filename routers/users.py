from fastapi import APIRouter, Depends, Request, HTTPException, status
from firebase_admin import auth
from fastapi.responses import JSONResponse

from dependencies import get_current_user, oauth2_scheme, ref
from models import CurrentUser, BaseUser
from datetime import date, datetime

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=CurrentUser)
async def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    today = date.today()
    birth = datetime.strptime(current_user["birthdate"], "%d/%m/%Y")
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return JSONResponse(content={
        "name": current_user["name"],
        "age": age,
        "gender": current_user["gender"],
        "profilePicUrl": current_user["profilePicUrl"],
        "email": current_user["email"]
    }, status_code=200)


@router.get("/friends")
async def get_friends(token: str = Depends(oauth2_scheme)):
    try:
        user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    friends_ref = ref.child("users").child(user["uid"]).child("friends")

    return JSONResponse(content=friends_ref.get(), status_code=200)


@router.put("/update")
async def update_user(request: Request, token: str = Depends(oauth2_scheme)):
    # todo:constraints on user data
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    uid = current_user["uid"]

    try:
        auth.update_user(
            uid,
            email=req_json["email"] if "email" in req_json else auth.get_user(uid).email,
            display_name=req_json["name"] if "name" in req_json else auth.get_user(uid).display_name
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect data",
        )

    user = ref.child("users").child(uid)

    if "email" in req_json:
        user.update({"email": req_json["email"]})
    if "date" in req_json:
        user.update({"birthdate": req_json["date"]})
    if "gender" in req_json and req_json["gender"] in ('m', 'f', 'nb', 'pns'):
        user.update({"gender": req_json["gender"]})
    if "name" in req_json:
        user.update({"name": req_json["name"]})
    if "profilePicUrl" in req_json:
        user.update({"profilePicUrl": req_json["profilePicUrl"]})

    return JSONResponse(content=user.get(), status_code=200)


@router.post("/preferences")
async def set_preferences(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    user_ref = ref.child("users").child(user["uid"])

    try:
        user_ref.update({
            'preferences': {
                'distance': req_json["distance"],
                'sex': req_json["sex"],
                'age_min': req_json["age_min"],
                'age_max': req_json["age_max"]
            }   
        })
        return JSONResponse(content=user_ref.get(), status_code=200)

    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect data",
        )


@router.post("/interests")
async def set_interests(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    user_ref = ref.child("users").child(user["uid"])

    try:
        user_ref.update({
            'interests': {
                'hobbies': req_json["hobbies"],
                'about': req_json["about"],
                'zodiac': req_json["zodiac"],
                'communication': req_json["communication"],
                'workout': req_json["workout"],
                'drinking': req_json["drinking"],
                'smoking': req_json["smoking"]
            }
        })
        return JSONResponse(content=user_ref.get(), status_code=200)

    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect data",
        )


@router.post("/friends")
async def add_friends(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    req_json = await request.json()
    if current_user["uid"] in (req_json["uid1"], req_json["uid2"]):
        user1_ref = ref.child("users").child(req_json["uid1"])
        user2_ref = ref.child("users").child(req_json["uid2"])
        friends1_ref = user1_ref.child("friends")
        friends2_ref = user2_ref.child("friends")
        try:
            friends1_ref.push({
                'uid': req_json["uid2"]
            })
            friends2_ref.push({
                'uid': req_json["uid1"]
            })
            return JSONResponse(content={'msg': 'Friends added'}, status_code=200)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect data",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect data",
        )


@router.get("/{uid}", response_model=BaseUser)
async def get_user(uid: str):
    try:
        user = ref.child("users").child(uid).get()
        return BaseUser(**user)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )