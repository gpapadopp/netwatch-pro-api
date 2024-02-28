from pydantic import BaseModel
from models.package_apks_model import PackageApks
from typing import List


class PackagePermissionsResponsePredict(BaseModel):
    status: str
    is_malware: bool
    package_prediction: str
    package_permission: PackageApks
    minimal_risk_permissions: List[str]
    low_risk_permissions: List[str]
    moderate_risk_permissions: List[str]
    high_risk_permissions: List[str]
    most_dangerous_permissions: List[str]
