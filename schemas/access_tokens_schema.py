
def access_tokens_serializer(access_token) -> dict:
    return {
        'id': str(access_token['_id']),
        'issuer': str(access_token['issuer']),
        'purpose': str(access_token['purpose']),
        'disabled': bool(access_token['disabled']),
        'api_key': str(access_token['api_key']),
        'secret_key': str(access_token['secret_key']),
        'active_until': str(access_token['active_until']),
        'access_models': list(access_token['access_models']),
        'created_at': str(access_token['created_at'])
    }


def all_access_tokens_serializer(access_tokens) -> list:
    return [access_tokens_serializer(single_access_token) for single_access_token in access_tokens]
