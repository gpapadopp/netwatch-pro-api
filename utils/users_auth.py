import utils.globals
import jwt


def check_login_token(token: str) -> bool:
    split_token = token.split(" ")
    try:
        jwt.decode(split_token[1], utils.globals.SECRET_KEY, algorithms=[utils.globals.ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.PyJWTError:
        return False
