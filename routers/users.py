from fastapi import APIRouter, Depends, Request, HTTPException, status
from firebase_admin import auth
from fastapi.responses import JSONResponse

from dependencies import get_current_user, oauth2_scheme, ref
from models import CurrentUser, BaseUser

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=CurrentUser)
async def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    return current_user


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


@router.put("/{uid}")
async def update_user(uid: str, request: Request, token: str = Depends(oauth2_scheme)):
    # todo:constraints on user data
    try:
        current_user = auth.verify_id_token(token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user["uid"] != uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action forbidden",
        )

    req_json = await request.json()
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
    if "age" in req_json:
        user.update({"age": req_json["age"]})
    if "gender" in req_json and req_json["gender"] in ('m', 'f', 'nb', 'pns'):
        user.update({"gender": req_json["gender"]})
    if "name" in req_json:
        user.update({"name": req_json["name"]})

    return JSONResponse(content=user.get(), status_code=200)