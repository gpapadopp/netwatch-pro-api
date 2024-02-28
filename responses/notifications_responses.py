from pydantic import BaseModel
from models.notifications_model import NotificationsModel
from typing import List


class NotificationsResponseAdd(BaseModel):
    status: str
    notification: NotificationsModel


class NotificationResponseIndex(BaseModel):
    status: str
    notifications: List[NotificationsModel]


class NotificationsResponseIndexWithPagination(BaseModel):
    status: str
    current_page: int
    current_results: int
    total_results: int
    notifications: List[NotificationsModel]


class NotificationsResponseView(BaseModel):
    status: str
    notification: NotificationsModel


class NotificationsResponseUpdate(BaseModel):
    status: str
    message: str


class NotificationsResponseUpdateBanner(BaseModel):
    status: str
    message: str
