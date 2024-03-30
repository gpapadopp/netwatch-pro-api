from pydantic import BaseModel
from response_models.malicious_files_signatures import MaliciousFilesSignaturesResponseModel
from typing import List, Optional


class MaliciousFilesSignaturesResponseAdd(BaseModel):
    success: bool
    message: Optional[str]
    malicious_file_signature: Optional[MaliciousFilesSignaturesResponseModel]


class MaliciousFilesSignaturesResponseIndexWithPagination(BaseModel):
    success: bool
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    malicious_file_signatures: Optional[List[MaliciousFilesSignaturesResponseModel]]


class MaliciousFilesSignaturesResponseView(BaseModel):
    success: bool
    message: Optional[str]
    malicious_file_signature: Optional[MaliciousFilesSignaturesResponseModel]


class MaliciousFilesSignaturesResponseEdit(BaseModel):
    success: bool
    message: Optional[str]


class MaliciousFilesSignaturesResponseDelete(BaseModel):
    success: bool
    message: Optional[str]