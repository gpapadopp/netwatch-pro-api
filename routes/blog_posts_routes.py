from bson import ObjectId
from fastapi import APIRouter, Form, Header, UploadFile, File, Query
from typing import Annotated
from models.blog_posts_model import BlogPosts
from schemas.blog_posts_schema import all_blog_posts_serializer
from config.db import DatabaseConnection
import utils.users_auth
import uuid
from fastapi.responses import FileResponse
from response_models.blog_post import BlogPostResponseModel
from response_models.blog_post import BlogPostAuthorDetails

from responses.blog_posts_responses import BlogPostsResponseAdd
from responses.blog_posts_responses import BlogPostsResponseIndex
from responses.blog_posts_responses import BlogPostsResponseView
from responses.blog_posts_responses import BlogPostsResponseUpdate
from responses.blog_posts_responses import BlogPostsResponseDelete

blog_post_api = APIRouter()


@blog_post_api.post("/v1/blog-posts/add", status_code=201, tags=['Blog Posts'], summary="Add Blog Post",
                    description="Endpoint to add a new blog post", response_model=BlogPostsResponseAdd)
async def add_blog_post(
        post_content: Annotated[str, Form()],
        post_title: Annotated[str, Form()],
        disabled: Annotated[bool, Form()],
        post_banner: UploadFile = File(...),
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return BlogPostsResponseAdd(success=False, message="unauthorized", blog_post=None)

    user_details = utils.users_auth.get_user_info(authorization)

    unique_filename = str(uuid.uuid4())
    banner_extension = post_banner.filename.split(".")[1]
    file_unique_name = unique_filename + "." + banner_extension
    file_location = f"files/blog_posts_banners/{file_unique_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(post_banner.file.read())

    blog_post_model = BlogPosts(
        post_author_id=str(user_details["_id"]),
        post_content=post_content,
        post_title=post_title,
        post_banner=file_unique_name,
        disabled=disabled
    )

    _id = DatabaseConnection.get_blog_posts_collection().insert_one(dict(blog_post_model))
    blog_post_details_db = all_blog_posts_serializer(
        DatabaseConnection.get_blog_posts_collection().find({"_id": _id.inserted_id}))

    inserted_user_details = DatabaseConnection.get_users_collection().find_one({"_id": user_details["_id"]})
    post_author_dict = {
        "first_name": inserted_user_details["first_name"],
        "last_name": inserted_user_details["last_name"],
        "email": inserted_user_details["email"],
    }

    response_blog_post = BlogPostResponseModel(
        id=blog_post_details_db[0]["id"],
        post_author_id=blog_post_details_db[0]["post_author_id"],
        post_content=blog_post_details_db[0]["post_content"],
        post_title=blog_post_details_db[0]["post_title"],
        post_banner=blog_post_details_db[0]["post_banner"],
        disabled=blog_post_details_db[0]["disabled"],
        created_at=blog_post_details_db[0]["created_at"],
        post_author_details=BlogPostAuthorDetails(
            first_name=inserted_user_details["first_name"],
            last_name=inserted_user_details["last_name"],
            email=inserted_user_details["email"]
        )
    )

    return BlogPostsResponseAdd(success=True, message=None, blog_post=response_blog_post)


@blog_post_api.get("/v1/blog-posts/", status_code=200, tags=['Blog Posts'], summary="Get All Blog Post",
                   description="Get All Blog Post", response_model=BlogPostsResponseIndex)
async def get_all_blog_posts(
        page: int = Query(..., description="Page number starting from 0"),
        limit: int = Query(..., description="Number of items per page"),
):
    blog_posts_details_db = all_blog_posts_serializer(
        DatabaseConnection.get_blog_posts_collection().find({}).sort("created_at", -1))

    if limit == -1:
        blog_posts_formatted = blog_posts_details_db
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        blog_posts_formatted = blog_posts_details_db[start_idx:end_idx]

    blog_posts_to_return = []
    for blog_post in blog_posts_formatted:
        post_user_details = DatabaseConnection.get_users_collection().find_one(
            {"_id": ObjectId(blog_post["post_author_id"])})
        single_post_response = BlogPostResponseModel(
            id=blog_post["id"],
            post_author_id=blog_post["post_author_id"],
            post_content=blog_post["post_content"],
            post_title=blog_post["post_title"],
            post_banner=blog_post["post_banner"],
            disabled=blog_post["disabled"],
            created_at=blog_post["created_at"],
            post_author_details=BlogPostAuthorDetails(
                first_name=post_user_details["first_name"],
                last_name=post_user_details["last_name"],
                email=post_user_details["email"]
            )
        )
        blog_posts_to_return.append(single_post_response)

    return BlogPostsResponseIndex(
        success=True,
        message=None,
        current_page=page,
        current_results=len(blog_posts_to_return),
        total_results=len(blog_posts_details_db),
        all_blog_posts=list(blog_posts_to_return)
    )


@blog_post_api.get("/v1/blog-posts/{blog_post_id}", status_code=200, tags=['Blog Posts'],
                   summary="Get Specific Blog Post", description="Get Specific Blog Post - By ID",
                   response_model=BlogPostsResponseView)
async def get_specific_blog_post(
        blog_post_id,
):
    try:
        blog_post_details_db = all_blog_posts_serializer(
            DatabaseConnection.get_blog_posts_collection().find({"_id": ObjectId(blog_post_id)}))

        if blog_post_details_db is None:
            return BlogPostsResponseView(success=False, message="Blog Post does NOT exists", blog_post=None)

        post_user_details = DatabaseConnection.get_users_collection().find_one(
            {"_id": ObjectId(blog_post_details_db[0]["post_author_id"])})
        single_post_response = BlogPostResponseModel(
            id=blog_post_details_db[0]["id"],
            post_author_id=blog_post_details_db[0]["post_author_id"],
            post_content=blog_post_details_db[0]["post_content"],
            post_title=blog_post_details_db[0]["post_title"],
            post_banner=blog_post_details_db[0]["post_banner"],
            disabled=blog_post_details_db[0]["disabled"],
            created_at=blog_post_details_db[0]["created_at"],
            post_author_details=BlogPostAuthorDetails(
                first_name=post_user_details["first_name"],
                last_name=post_user_details["last_name"],
                email=post_user_details["email"]
            )
        )

        return BlogPostsResponseView(success=True, message=None, blog_post=single_post_response)
    except Exception as ex:
        return BlogPostsResponseView(success=False, message="Blog Post does NOT exists", blog_post=None)


@blog_post_api.get("/v1/blog-posts/get-banner/{blog_post_id}", status_code=200, tags=['Blog Posts'],
                   summary="Get the Blog Post's Banner", description="Get the Blog Post's Banner File",
                   response_class=FileResponse)
async def get_specific_notification_banner(blog_post_id):
    try:
        blog_post_object_id = ObjectId(blog_post_id)
        existing_blog_post = DatabaseConnection.get_blog_posts_collection().find_one({"_id": blog_post_object_id})

        if existing_blog_post is None:
            return {
                "success": False,
                "message": "Notification does NOT exists"
            }

        file_location = f"files/blog_posts_banners/{existing_blog_post['post_banner']}"
        return file_location
    except Exception as ex:
        return {
            "success": False,
            "message": "Notification does NOT exists"
        }


@blog_post_api.post("/v1/blog-posts/{blog_post_id}", status_code=200, tags=['Blog Posts'],
                    summary="Update Specific Blog Post", description="Update Specific Blog Post - By ID",
                    response_model=BlogPostsResponseUpdate)
async def update_specific_blog_post(
        blog_post_id,
        post_content: Annotated[str, Form()],
        post_title: Annotated[str, Form()],
        disabled: Annotated[bool, Form()],
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return BlogPostsResponseUpdate(success=False, message="unauthorized")

    try:
        blog_post_object_id = ObjectId(blog_post_id)
        existing_blog_post = DatabaseConnection.get_blog_posts_collection().find_one({"_id": blog_post_object_id})

        if existing_blog_post is None:
            return BlogPostsResponseUpdate(success=False, message="Blog Post not exists")

        existing_blog_post['post_content'] = post_content
        existing_blog_post['post_title'] = post_title
        existing_blog_post['disabled'] = disabled

        DatabaseConnection.get_blog_posts_collection().update_one({"_id": blog_post_object_id},
                                                                  {"$set": existing_blog_post})

        return BlogPostsResponseUpdate(success=True, message="Blog Post Updated Successfully")
    except Exception as ex:
        return BlogPostsResponseUpdate(success=False, message="There was an error during blog post update")


@blog_post_api.post("/v1/blog-posts/change-banner/{blog_post_id}", status_code=200, tags=['Blog Posts'],
                    summary="Update Specific Blog Post Banner", description="Update Specific Blog Post Banner - By ID",
                    response_model=BlogPostsResponseUpdate)
async def update_specific_blog_post_banner(
        blog_post_id,
        post_banner: UploadFile = File(...),
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return BlogPostsResponseUpdate(success=False, message="unauthorized")

    try:
        blog_post_object_id = ObjectId(blog_post_id)
        existing_blog_post = DatabaseConnection.get_blog_posts_collection().find_one({"_id": blog_post_object_id})

        if existing_blog_post is None:
            return BlogPostsResponseUpdate(success=False, message="Blog Post not exists")

        unique_filename = str(uuid.uuid4())
        banner_extension = post_banner.filename.split(".")[1]
        file_unique_name = unique_filename + "." + banner_extension
        file_location = f"files/blog_posts_banners/{file_unique_name}"
        with open(file_location, "wb+") as file_object:
            file_object.write(post_banner.file.read())

        existing_blog_post['post_banner'] = file_unique_name
        DatabaseConnection.get_blog_posts_collection().update_one({"_id": blog_post_object_id},
                                                                  {"$set": existing_blog_post})

        return BlogPostsResponseUpdate(success=True, message="Blog Post Updated Successfully")
    except Exception as ex:
        return BlogPostsResponseUpdate(success=False, message="There was an error during blog post update")


@blog_post_api.delete("/v1/blog-posts/{blog_post_id}", status_code=200, tags=['Blog Posts'],
                      summary="Delete Specific Blog Post", description="Delete Specific Blog Post - By ID",
                      response_model=BlogPostsResponseDelete)
async def delete_specific_blog_post(
        blog_post_id,
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return BlogPostsResponseDelete(success=False, message="unauthorized")

    try:
        blog_post_object_id = ObjectId(blog_post_id)
        DatabaseConnection.get_blog_posts_collection().delete_one({"_id": blog_post_object_id})

        return BlogPostsResponseDelete(success=True, message="Blog Post Deleted Successfully")
    except Exception as ex:
        return BlogPostsResponseDelete(success=False, message="There was an error during blog post deletion")
