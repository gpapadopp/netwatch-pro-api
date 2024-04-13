from pydantic import BaseModel
from responses.authentication_responses import AuthenticationResponse
from response_models.user import UsersResponseModel
from typing import Optional, List


class UsersResponseAdd(BaseModel):
    success: bool
    message: Optional[str]
    user: Optional[UsersResponseModel]


class UsersResponseLogin(BaseModel):
    success: bool
    message: Optional[str]
    authentication: Optional[AuthenticationResponse]


class UsersResponseIndex(BaseModel):
    success: bool
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    all_users: Optional[List[UsersResponseModel]]


class UsersResponseView(BaseModel):
    success: bool
    message: Optional[str]
    user_details: Optional[UsersResponseModel]


class UsersResponseUpdate(BaseModel):
    success: bool
    message: str


class UsersResponseUpdatePassword(BaseModel):
    success: bool
    message: str
