
def users_serializer(user) -> dict:
    return {
        'id': str(user['_id']),
        'username': str(user['username']),
        'password': str(user['password']),
        'first_name': str(user['first_name']),
        'last_name': str(user['last_name']),
        'email': str(user['email']),
        'disabled': bool(user['disabled']),
        'created_at': str(user['created_at'])
    }


def all_users_serializer(users) -> list:
    return [users_serializer(single_user) for single_user in users]
