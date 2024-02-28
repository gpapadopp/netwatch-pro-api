from pydantic import BaseModel
from models.internet_packages_model import InternetPackages


class InternetPackagesAdd(BaseModel):
    status: str
    internet_package: InternetPackages
