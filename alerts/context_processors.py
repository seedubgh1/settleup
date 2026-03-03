from alerts.models import Alert


def unread_alert_count(request):
    """
    Injects unread_alert_count into every template context.
    Returns 0 if the user is not authenticated.
    """
    if not request.user.is_authenticated:
        return {"unread_alert_count": 0}

    count = Alert.objects.filter(
        recipient__user=request.user,
        is_read=False,
    ).count()

    return {"unread_alert_count": count}
