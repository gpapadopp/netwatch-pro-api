from typing import Optional, List
from response_models.package_apk import PackageApksResponseModel
from pydantic import BaseModel


class PackageApksResponsePredict(BaseModel):
    success: bool
    message: Optional[str]
    is_malware: Optional[bool]
    package_apk: Optional[PackageApksResponseModel]


class PackageApksResponseIndexWithPagination(BaseModel):
    success: bool
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    all_package_apks: Optional[List[PackageApksResponseModel]]


class PackageApksResponseView(BaseModel):
    success: bool
    message: Optional[str]
    package_apk: Optional[PackageApksResponseModel]


class PackageApksResponseEdit(BaseModel):
    success: bool
    message: Optional[str]


class PackageApksResponseDelete(BaseModel):
    success: bool
    message: Optional[str]
