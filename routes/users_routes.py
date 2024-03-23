from fastapi import APIRouter, Form, Header, Query
from typing import Annotated
from models.users_model import UsersModel
from datetime import datetime, timedelta
from responses.authentication_responses import AuthenticationResponse
from schemas.users_schema import all_users_serializer
from config.db import DatabaseConnection
from passlib.context import CryptContext
import utils.globals
import utils.users_auth
import jwt
from bson import ObjectId
from responses.users_responses import UsersResponseAdd
from responses.users_responses import UsersResponseLogin
from responses.users_responses import UsersResponseIndex
from responses.users_responses import UsersResponseView
from responses.users_responses import UsersResponseUpdate
from responses.users_responses import UsersResponseUpdatePassword

users_api = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@users_api.post('/v1/users/add', status_code=201, tags=['Users'], summary="Add new User", description="Add a new user", response_model=UsersResponseAdd)
async def add_user(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        first_name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        disabled: Annotated[bool, Form()],
        authorization: str = Header(..., description="Bearer Token"),
):
    if not utils.users_auth.check_login_token(authorization):
        return UsersResponseAdd(success=False, message="unauthorized", user=None)

    user_model = UsersModel(
        username=username,
        password=pwd_context.hash(password),
        first_name=first_name,
        last_name=last_name,
        email=email,
        disabled=disabled
    )

    _id = DatabaseConnection.get_users_collection().insert_one(dict(user_model))
    user_details_db = all_users_serializer(
        DatabaseConnection.get_users_collection().find({"_id": _id.inserted_id}))

    return UsersResponseAdd(success=True, message=None, user=user_details_db[0])

@users_api.post("/v1/users/login", status_code=200, tags=['Users'], summary="Login User", description="Authenticate a user", response_model=UsersResponseLogin)
async def login_user(
    username: str = Form(...),
    password: str = Form(...),
):
    existing_user = DatabaseConnection.get_users_collection().find_one({"username": username})
    if existing_user is None:
        return UsersResponseLogin(success=False, message="Wrong username/password", authentication=None)

    if not pwd_context.verify(password, existing_user["password"]):
        return UsersResponseLogin(success=False, message="Wrong username/password", authentication=None)

    expiration_date = datetime.now() + timedelta(minutes=utils.globals.ACCESS_TOKEN_EXPIRE_MINUTES)

    created_at_iso = existing_user['created_at'].isoformat()
    issue_time_iso = datetime.now().isoformat()
    expiration_date_iso = expiration_date.isoformat()

    data_to_encode = {
        "username": existing_user['username'],
        "first_name": existing_user['first_name'],
        "last_name": existing_user['last_name'],
        "email": existing_user['email'],
        "disabled": existing_user['disabled'],
        "created_at": created_at_iso,
        "issue_time": issue_time_iso,
        "expiration": expiration_date_iso
    }
    encoded_jwt = jwt.encode(data_to_encode, utils.globals.SECRET_KEY, algorithm=utils.globals.ALGORITHM)

    authentication_response = AuthenticationResponse(token=encoded_jwt, type="bearer")

    return UsersResponseLogin(success=True, message=None, authentication=authentication_response)


@users_api.get("/v1/users/", status_code=200, tags=['Users'], summary="Get All Users", description="Get All Users with Pagination", response_model=UsersResponseIndex)
async def get_all_users(
        page: int = Query(..., description="Page number starting from 0"),
        limit: int = Query(..., description="Number of items per page"),
        authorization: str = Header(..., description="Bearer Token"),
):
    if not utils.users_auth.check_login_token(authorization):
        return UsersResponseIndex(success=False, message="unauthorized", current_page=0, current_results=0, total_results=0, all_users=None)

    users_db = all_users_serializer(DatabaseConnection.get_users_collection().find({}))
    if limit == -1:
        return UsersResponseIndex(success=True, message=None, current_page=1, current_results=len(users_db),
                                  total_results=len(users_db), all_users=users_db)
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        users_to_return = users_db[start_idx:end_idx]
        return UsersResponseIndex(success=True, message=None, current_page=page, current_results=len(users_to_return),
                                  total_results=len(users_to_return), all_users=users_to_return)


@users_api.get("/v1/users/{user_id}", status_code=200, tags=['Users'], summary="Get Specific User", description="Get Specific User - By ID", response_model=UsersResponseView)
async def get_specific_user(
        user_id,
        authorization: str = Header(..., description="Bearer Token"),
):
    if not utils.users_auth.check_login_token(authorization):
        return UsersResponseView(success=False, message="unauthorized", user_details=None)

    try:
        user_details_db = all_users_serializer(
            DatabaseConnection.get_users_collection().find({"_id": ObjectId(user_id)}))

        return UsersResponseView(success=True, message=None, user_details=user_details_db[0])
    except Exception as ex:
        return UsersResponseView(success=False, message="User does NOT exists", user_details=None)


@users_api.post("/v1/users/{user_id}", status_code=200, tags=['Users'], summary="Update Specific User", description="Update Specific User - By ID", response_model=UsersResponseUpdate)
async def update_specific_user(
        user_id,
        username: Annotated[str, Form()],
        first_name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        disabled: Annotated[bool, Form()],
        authorization: str = Header(..., description="Bearer Token"),
):
    if not utils.users_auth.check_login_token(authorization):
        return UsersResponseUpdate(success=False, message="unauthorized")

    try:
        user_object_id = ObjectId(user_id)
        existing_user = DatabaseConnection.get_users_collection().find_one({"_id": user_object_id})

        if existing_user is None:
            return UsersResponseUpdate(success=False, message="User not Exists")

        existing_user['username'] = username
        existing_user['first_name'] = first_name
        existing_user['last_name'] = last_name
        existing_user['email'] = email
        existing_user['disabled'] = disabled

        DatabaseConnection.get_users_collection().update_one({"_id": user_object_id}, {"$set": existing_user})

        return UsersResponseUpdate(success=True, message="User Updated Successfully")
    except Exception as ex:
        return UsersResponseUpdate(success=False, message="User not Exists")


@users_api.post("/v1/users/change-password/{user_id}", status_code=200, tags=['Users'], summary="Update User's password", description="Update Specific User's Password - By ID", response_model=UsersResponseUpdatePassword)
async def update_password_specific_user(
        user_id,
        password: Annotated[str, Form()],
        authorization: str = Header(..., description="Bearer Token"),
):
    if not utils.users_auth.check_login_token(authorization):
        return UsersResponseUpdatePassword(success=False, message="unauthorized")

    try:
        user_object_id = ObjectId(user_id)
        existing_user = DatabaseConnection.get_users_collection().find_one({"_id": user_object_id})

        if existing_user is None:
            return UsersResponseUpdatePassword(success=False, message="User not exists")

        existing_user['password'] = pwd_context.hash(password)

        DatabaseConnection.get_users_collection().update_one({"_id": user_object_id}, {"$set": existing_user})

        return UsersResponseUpdatePassword(success=True, message="User Updated Successfully")
    except Exception as ex:
        return UsersResponseUpdatePassword(success=False, message="User not exists")
