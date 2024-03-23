from pydantic import BaseModel
from response_models.notification import NotificationResponseModel
from typing import List, Optional


class NotificationsResponseAdd(BaseModel):
    success: bool
    message: Optional[str]
    notification: Optional[NotificationResponseModel]


class NotificationResponseIndex(BaseModel):
    success: bool
    message: Optional[str]
    notifications: Optional[List[NotificationResponseModel]]


class NotificationsResponseIndexWithPagination(BaseModel):
    success: bool
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    notifications: Optional[List[NotificationResponseModel]]


class NotificationsResponseView(BaseModel):
    success: bool
    message: Optional[str]
    notification: Optional[NotificationResponseModel]


class NotificationsResponseUpdate(BaseModel):
    success: bool
    message: str


class NotificationsResponseUpdateBanner(BaseModel):
    success: bool
    message: str


class NotificationsResponseDelete(BaseModel):
    success: bool
    message: str
