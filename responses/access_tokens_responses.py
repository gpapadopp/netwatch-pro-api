from pydantic import BaseModel
from typing import List
from models.access_tokens_model import AccessTokensModel


class AccessTokensResponseAdd(BaseModel):
    status: str
    access_token: List[AccessTokensModel]


class AccessTokensResponseIndex(BaseModel):
    status: str
    current_page: int
    current_results: int
    total_results: int
    all_access_tokens: List[AccessTokensModel]


class AccessTokensResponseView(BaseModel):
    status: str
    access_token_details: AccessTokensModel


class AccessTokenResponseUpdate(BaseModel):
    status: str
    message: str


class AccessTokenResponseDelete(BaseModel):
    status: str
    message: str
