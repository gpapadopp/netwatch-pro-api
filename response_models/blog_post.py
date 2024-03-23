from datetime import datetime
from pydantic import BaseModel


class BlogPostAuthorDetails(BaseModel):
    first_name: str
    last_name: str
    email: str


class BlogPostResponseModel(BaseModel):
    id: str
    post_author_id: str
    post_content: str
    post_title: str
    post_banner: str
    disabled: bool
    created_at: datetime
    post_author_details: BlogPostAuthorDetails
