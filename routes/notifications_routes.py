from fastapi import APIRouter, UploadFile, File, Form, Header, Query
from typing import Annotated
from models.notifications_model import NotificationsModel
from schemas.notifications_schema import all_notifications_serializer
from config.db import notifications_collection
import utils.users_auth
import uuid
from bson import ObjectId
from fastapi.responses import FileResponse
from responses.notifications_responses import NotificationResponseIndex
from responses.notifications_responses import NotificationsResponseAdd
from responses.notifications_responses import NotificationsResponseIndexWithPagination
from responses.notifications_responses import NotificationsResponseView
from responses.notifications_responses import NotificationsResponseUpdate
from responses.notifications_responses import NotificationsResponseUpdateBanner

notification_api = APIRouter()


@notification_api.post("/v1/notifications/add", status_code=201, tags=['Notifications'], summary="Add Notification", description="Add a New Notification", response_model=NotificationsResponseAdd)
async def add_notification(
    title: Annotated[str, Form()],
    context: Annotated[str, Form()],
    disabled: Annotated[bool, Form()],
    banner: UploadFile = File(...),
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    unique_filename = str(uuid.uuid4())
    banner_extension = banner.filename.split(".")[1]
    file_unique_name = unique_filename + "." + banner_extension
    file_location = f"files/notification_banners/{file_unique_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(banner.file.read())

    notification_model = NotificationsModel(
        title=title,
        context=context,
        disabled=disabled,
        banner=file_unique_name
    )

    _id = notifications_collection.insert_one(dict(notification_model))
    notification_details_db = all_notifications_serializer(
        notifications_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "notification": notification_details_db
    }


@notification_api.get("/v1/notifications/", status_code=200, tags=['Notifications'], summary="Get All Notifications", description="Get All Notifications", response_model=NotificationResponseIndex)
async def get_all_notifications():
    notification_details_db = all_notifications_serializer(notifications_collection.find({}).sort("created_at", -1))
    return {
        "status": "success",
        "notifications": notification_details_db
    }


@notification_api.get("/v1/notifications/with-pagination", status_code=200, tags=['Notifications'], summary="Get All Notifications with Pagination", description="Get All Notifications with Pagination", response_model=NotificationsResponseIndexWithPagination)
async def get_all_notifications_with_pagination(
    page: int = Query(..., description="Page number starting from 0"),
    limit: int = Query(..., description="Number of items per page"),
):
    notification_details_db = all_notifications_serializer(notifications_collection.find({}))
    if limit == -1:
        return {
            "status": "success",
            "current_page": 1,
            "current_results": len(notification_details_db),
            "total_results": len(notification_details_db),
            "notifications": notification_details_db
        }
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        notifications_to_return = notification_details_db[start_idx:end_idx]
        return {
            "status": "success",
            "current_page": page,
            "current_results": len(notifications_to_return),
            "total_results": len(notification_details_db),
            "notifications": notifications_to_return
        }


@notification_api.get("/v1/notifications/{notification_id}", status_code=200, tags=['Notifications'], summary="Get Specific Notification", description="Get Specific Notification - By ID", response_model=NotificationsResponseView)
async def get_specific_notification(notification_id):
    notification_details_db = all_notifications_serializer(
        notifications_collection.find({"_id": ObjectId(notification_id)}))
    return {
        "status": "success",
        "notification": notification_details_db
    }


@notification_api.get("/v1/notifications/get-banner/{notification_id}", status_code=200, tags=['Notifications'], summary="Get the Notification Banner", description="Get the Notification Banner File", response_class=FileResponse)
async def get_specific_notification_banner(notification_id):
    notification_object_id = ObjectId(notification_id)
    existing_notification = notifications_collection.find_one({"_id": notification_object_id})

    if existing_notification is None:
        return {
            "status": "error",
            "message": "Notification does NOT exists"
        }

    file_location = f"files/notification_banners/{existing_notification['banner']}"
    return file_location


@notification_api.post("/v1/notifications/{notification_id}", status_code=200, tags=['Notifications'], summary="Update Specific Notification", description="Update Specific Notification - By ID", response_model=NotificationsResponseUpdate)
async def update_specific_notification(
    notification_id,
    title: Annotated[str, Form()],
    context: Annotated[str, Form()],
    disabled: Annotated[bool, Form()],
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    notification_object_id = ObjectId(notification_id)
    existing_notification = notifications_collection.find_one({"_id": notification_object_id})

    if existing_notification is None:
        return {
            "status": "error",
            "message": "Notification does NOT exists"
        }

    existing_notification['title'] = title
    existing_notification['context'] = context
    existing_notification['disabled'] = disabled

    notifications_collection.update_one({"_id": notification_object_id}, {"$set": existing_notification})

    return {
        "status": "success",
        "message": "Notification Updated Successfully"
    }


@notification_api.post("/v1/notifications/change-banner/{notification_id}", status_code=200, tags=['Notifications'], summary="Update Specific Notification Banner", description="Update Specific Notification Banner - By ID", response_model=NotificationsResponseUpdateBanner)
async def update_specific_notification_banner(
    notification_id,
    banner: UploadFile = File(...),
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    notification_object_id = ObjectId(notification_id)
    existing_notification = notifications_collection.find_one({"_id": notification_object_id})

    if existing_notification is None:
        return {
            "status": "error",
            "message": "Notification does NOT exists"
        }

    unique_filename = str(uuid.uuid4())
    banner_extension = banner.filename.split(".")[1]
    file_unique_name = unique_filename + "." + banner_extension
    file_location = f"files/notification_banners/{file_unique_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(banner.file.read())

    existing_notification['banner'] = file_unique_name
    notifications_collection.update_one({"_id": notification_object_id}, {"$set": existing_notification})

    return {
        "status": "success",
        "message": "Notification Updated Successfully"
    }
