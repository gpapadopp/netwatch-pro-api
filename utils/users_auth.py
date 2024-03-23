import utils.globals
import jwt
from config.db import DatabaseConnection


def check_login_token(token: str) -> bool:
    split_token = token.split(" ")
    try:
        jwt.decode(split_token[1], utils.globals.SECRET_KEY, algorithms=[utils.globals.ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.PyJWTError:
        return False


def get_user_info(token: str) -> dict:
    split_token = token.split(" ")
    decoded_user = jwt.decode(split_token[1], utils.globals.SECRET_KEY, algorithms=[utils.globals.ALGORITHM])
    user_details = DatabaseConnection.get_users_collection().find_one({"username": decoded_user["username"]})
    return user_details
