
def malicious_files_signatures_serializer(malicious_file) -> dict:
    return {
        'id': str(malicious_file['_id']),
        'file_signature': str(malicious_file['file_signature']),
        'file_signature_type': str(malicious_file['file_signature_type']),
        'file_category': str(malicious_file['file_category']),
        'created_at': malicious_file['created_at']
    }


def all_malicious_files_signatures_serializer(malicious_files_signatures) -> list:
    return [malicious_files_signatures_serializer(single_malicious_file) for single_malicious_file in malicious_files_signatures]
