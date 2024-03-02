from typing import Optional
from pydantic import BaseModel
from response_models.internet_package import InternetPackagesResponseModel


class InternetPackagesAdd(BaseModel):
    success: bool
    message: Optional[str]
    internet_package: InternetPackagesResponseModel
