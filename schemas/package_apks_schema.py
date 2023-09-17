def package_apks_serializer(package_apk) -> dict:
    return {
        'id': str(package_apk['_id']),
        'device_token': str(package_apk['device_token']),
        'package_name': str(package_apk['package_name']),
        'app_name': str(package_apk['app_name']),
        'apk_file': str(package_apk['apk_file']),
        'is_malware': str(package_apk['is_malware']),
        'created_at': str(package_apk['created_at'])
    }


def all_package_apks_serializer(package_apks) -> list:
    return [package_apks_serializer(package_apk) for package_apk in package_apks]
