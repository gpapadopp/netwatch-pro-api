def internet_packages_serializer(internet_package) -> dict:
    return {
        'id': str(internet_package['_id']),
        'device_token': str(internet_package['device_token']),
        'source_ip': str(internet_package['source_ip']),
        'destination_ip': str(internet_package['destination_ip']),
        'source_mac_address': str(internet_package['source_mac_address']),
        'destination_mac_address': str(internet_package['destination_mac_address']),
        'header_type': str(internet_package['header_type']),
        'raw_header': str(internet_package['raw_header']),
        'raw_payload': str(internet_package['raw_payload']),
        'created_at': str(internet_package['created_at']),
        'access_token_id': str(internet_package['access_token_id'])
    }


def all_internet_packages_serializer(internet_packages) -> list:
    return [internet_packages_serializer(internet_package) for internet_package in internet_packages]
