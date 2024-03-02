def package_apks_serializer(package_apk) -> dict:
    return {
        'id': str(package_apk['_id']),
        'device_token': str(package_apk['device_token']),
        'package_name': str(package_apk['package_name']),
        'app_name': str(package_apk['app_name']),
        'apk_file': str(package_apk['apk_file']),
        'is_malware': None if package_apk['is_malware'] is None else str(package_apk['is_malware']),
        'created_at': str(package_apk['created_at']),
        'md5_checksum': str(package_apk['md5_checksum']),
        'access_token_id': str(package_apk['access_token_id'])
    }


def all_package_apks_serializer(package_apks) -> list:
    return [package_apks_serializer(package_apk) for package_apk in package_apks]
