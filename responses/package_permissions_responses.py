from pydantic import BaseModel
from response_models.package_permission import PackagePermissionsResponseModel
from typing import List, Optional


class PackagePermissionsResponsePredict(BaseModel):
    success: bool
    message: Optional[str]
    is_malware: Optional[bool]
    package_prediction: Optional[str]
    package_permission: Optional[PackagePermissionsResponseModel]
    minimal_risk_permissions: Optional[List[str]]
    low_risk_permissions: Optional[List[str]]
    moderate_risk_permissions: Optional[List[str]]
    high_risk_permissions: Optional[List[str]]
    most_dangerous_permissions: Optional[List[str]]
