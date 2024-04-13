from pydantic import BaseModel
from response_models.blog_post import BlogPostResponseModel
from typing import Optional, List


class BlogPostsResponseAdd(BaseModel):
    success: bool
    message: Optional[str]
    blog_post: Optional[BlogPostResponseModel]


class BlogPostsResponseIndex(BaseModel):
    success: bool
    message: Optional[str]
    current_page: int
    current_results: int
    total_results: int
    all_blog_posts: Optional[List[BlogPostResponseModel]]


class BlogPostsResponseView(BaseModel):
    success: bool
    message: Optional[str]
    blog_post: Optional[BlogPostResponseModel]


class BlogPostsResponseUpdate(BaseModel):
    success: bool
    message: str


class BlogPostsResponseDelete(BaseModel):
    success: bool
    message: str
