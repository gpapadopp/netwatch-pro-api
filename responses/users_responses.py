from pydantic import BaseModel
from models.users_model import UsersModel
from responses.authentication_responses import AuthenticationResponse


class UsersResponseAdd(BaseModel):
    status: str
    user: UsersModel


class UsersResponseLogin(BaseModel):
    status: str
    authentication: AuthenticationResponse


class UsersResponseIndex(BaseModel):
    status: str
    current_page: int
    current_results: int
    total_results: int
    all_users: UsersModel


class UsersResponseView(BaseModel):
    status: str
    user_details: UsersModel


class UsersResponseUpdate(BaseModel):
    status: str
    message: str


class UsersResponseUpdatePassword(BaseModel):
    status: str
    message: str
