from fastapi import APIRouter, Form
from typing import Annotated
from models.internet_packages_model import InternetPackages
from schemas.internet_packages_schema import all_internet_packages_serializer
from config.db import internet_packages_collection

internet_package = APIRouter()


@internet_package.post("/v1/internet-packages/add", status_code=201)
async def add_internet_package(
    device_token: Annotated[str, Form()],
    source_ip: Annotated[str, Form()],
    destination_ip: Annotated[str, Form()],
    source_mac_address: Annotated[str, Form()],
    destination_mac_address: Annotated[str, Form()],
    header_type: Annotated[str, Form()],
    raw_header: Annotated[str, Form()],
    raw_payload: Annotated[str, Form()],
):
    internet_package_model = InternetPackages(
        device_token=device_token,
        source_ip=source_ip,
        destination_ip=destination_ip,
        source_mac_address=source_mac_address,
        destination_mac_address=destination_mac_address,
        header_type=header_type,
        raw_header=raw_header,
        raw_payload=raw_payload
    )

    _id = internet_packages_collection.insert_one(dict(internet_package_model))
    internet_package_details_db = all_internet_packages_serializer(
        internet_packages_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "internet_package": internet_package_details_db
    }
