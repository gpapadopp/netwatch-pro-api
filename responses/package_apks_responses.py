from typing import Optional
from response_models.package_apk import PackageApksResponseModel
from pydantic import BaseModel


class PackageApksResponsePredict(BaseModel):
    success: bool
    message: Optional[str]
    is_malware: Optional[bool]
    package_apk: Optional[PackageApksResponseModel]
