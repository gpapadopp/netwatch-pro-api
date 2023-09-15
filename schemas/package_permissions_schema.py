def package_permissions_serializer(package_permission) -> dict:
    return {
        'id': str(package_permission['_id']),
        'device_token': str(package_permission['device_token']),
        'package_name': str(package_permission['package_name']),
        'app_name': str(package_permission['app_name']),
        'permissions': list(package_permission['permissions']),
        'certificate_subjects': list(package_permission['certificate_subjects']),
        'certificate_issuers': list(package_permission['certificate_issuers']),
        'certificate_serial_numbers': list(package_permission['certificate_serial_numbers']),
        'certificate_versions': list(package_permission['certificate_versions']),
        'is_malware': str(package_permission['is_malware']),
        'created_at': str(package_permission['created_at'])
    }


def all_package_permissions_serializer(package_permissions) -> list:
    return [package_permissions_serializer(package_permission) for package_permission in package_permissions]
