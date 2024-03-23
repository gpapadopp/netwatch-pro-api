
def blog_posts_serializer(blog_post) -> dict:
    return {
        'id': str(blog_post['_id']),
        'post_author_id': str(blog_post['post_author_id']),
        'post_content': str(blog_post['post_content']),
        'post_title': str(blog_post['post_title']),
        'post_banner': str(blog_post['post_banner']),
        'disabled': bool(blog_post['disabled']),
        'created_at': bool(blog_post['created_at'])
    }


def all_blog_posts_serializer(blog_posts) -> list:
    return [blog_posts_serializer(single_blog_post) for single_blog_post in blog_posts]
