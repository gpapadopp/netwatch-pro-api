from pydantic import BaseModel
from typing import List, Optional
from response_models.access_token import AccessTokenResponseModel


class AccessTokensResponseAdd(BaseModel):
    success: bool
    message: Optional[str]
    access_token: List[AccessTokenResponseModel]


class AccessTokensResponseIndex(BaseModel):
    success: int
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    all_access_tokens: Optional[List[AccessTokenResponseModel]]


class AccessTokensResponseView(BaseModel):
    success: bool
    message: Optional[str]
    access_token_details: Optional[AccessTokenResponseModel]


class AccessTokenResponseUpdate(BaseModel):
    success: bool
    message: Optional[str]


class AccessTokenResponseDelete(BaseModel):
    success: bool
    message: Optional[str]
