from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated
from models.notifications_model import NotificationsModel
from schemas.notifications_schema import all_notifications_serializer
from config.db import notifications_collection
import uuid
from bson import ObjectId
from fastapi.responses import FileResponse

notification_api = APIRouter()


@notification_api.post("/api/v1/notifications/add", status_code=201)
async def add_notification(
        title: Annotated[str, Form()],
        context: Annotated[str, Form()],
        disabled: Annotated[bool, Form()],
        banner: UploadFile = File(...),
):
    unique_filename = str(uuid.uuid4())
    banner_extension = banner.filename.split(".")[1]
    file_unique_name = unique_filename + "." + banner_extension
    file_location = f"notification_banners/{file_unique_name}"
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


@notification_api.get("/api/v1/notifications/", status_code=200)
async def get_all_notifications():
    notification_details_db = all_notifications_serializer(notifications_collection.find({}))
    return {
        "status": "success",
        "notifications": notification_details_db
    }


@notification_api.get("/api/v1/notifications/{notification_id}", status_code=200)
async def get_specific_notification(notification_id):
    notification_details_db = all_notifications_serializer(
        notifications_collection.find({"_id": ObjectId(notification_id)}))
    return {
        "status": "success",
        "notification": notification_details_db
    }


@notification_api.get("/api/v1/notifications/get-banner/{notification_id}", status_code=200,
                      response_class=FileResponse)
async def get_specific_notification_banner(notification_id):
    notification_object_id = ObjectId(notification_id)
    existing_notification = notifications_collection.find_one({"_id": notification_object_id})

    if existing_notification is None:
        return {
            "status": "error",
            "message": "Notification does NOT exists"
        }

    file_location = f"notification_banners/{existing_notification['banner']}"
    return file_location


@notification_api.post("/api/v1/notifications/{notification_id}", status_code=200)
async def update_specific_notification(
        notification_id,
        title: Annotated[str, Form()],
        context: Annotated[str, Form()],
        disabled: Annotated[bool, Form()]
):
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


@notification_api.post("/api/v1/notifications/change-banner/{notification_id}", status_code=200)
async def update_specific_notification_banner(
        notification_id,
        banner: UploadFile = File(...),
):
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
    file_location = f"notification_banners/{file_unique_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(banner.file.read())

    existing_notification['banner'] = file_unique_name
    notifications_collection.update_one({"_id": notification_object_id}, {"$set": existing_notification})

    return {
        "status": "success",
        "message": "Notification Updated Successfully"
    }
