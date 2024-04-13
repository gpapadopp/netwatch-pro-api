from typing import Optional, List
from pydantic import BaseModel
from response_models.internet_package import InternetPackagesResponseModel


class InternetPackagesResponseAdd(BaseModel):
    success: bool
    message: Optional[str]
    internet_package: Optional[InternetPackagesResponseModel]


class InternetPackagesResponseIndex(BaseModel):
    success: bool
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    all_internet_packages: Optional[List[InternetPackagesResponseModel]]


class InternetPackagesResponseView(BaseModel):
    success: bool
    message: Optional[str]
    internet_package: Optional[InternetPackagesResponseModel]


class InternetPackagesResponseUpdate(BaseModel):
    success: bool
    message: str


class InternetPackagesResponseDelete(BaseModel):
    success: bool
    message: str
