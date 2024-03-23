from datetime import datetime
from pydantic import BaseModel


class BlogPosts(BaseModel):
    post_author_id: str
    post_content: str
    post_title: str
    post_banner: str
    disabled: bool = False
    created_at: datetime = datetime.utcnow()
