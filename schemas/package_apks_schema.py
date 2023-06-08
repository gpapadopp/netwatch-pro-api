from fastapi import File


def package_apks_serializer(package_permission) -> dict:
    return {
        'id': str(package_permission['_id']),
        'device_token': str(package_permission['device_token']),
        'package_name': str(package_permission['package_name']),
        'app_name': str(package_permission['app_name']),
        'apk_file': str(package_permission['apk_file']),
        'created_at': str(package_permission['created_at'])
    }


def all_package_apks_serializer(package_apks) -> list:
    return [package_apks_serializer(package_apk) for package_apk in package_apks]
