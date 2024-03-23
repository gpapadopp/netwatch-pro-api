
def notifications_serializer(notification) -> dict:
    return {
        'id': str(notification['_id']),
        'title': str(notification['title']),
        'context': str(notification['context']),
        'banner': str(notification['banner']),
        'disabled': bool(notification['disabled']),
        'created_at': notification['created_at']
    }


def all_notifications_serializer(notifications) -> list:
    return [notifications_serializer(single_notification) for single_notification in notifications]
