from .consumers import (
                        NotificationForUser,
                        UnReadNotificationCount,
                        GetLastThirtyNotification,
                        NotificationCount
)
from django.urls import path
websocket_urlpatterns = [
    path('user', NotificationForUser.as_asgi()),
    path('unread/notification/count', UnReadNotificationCount.as_asgi()),
    path('last/thirty/notification', GetLastThirtyNotification.as_asgi()),
    path('count', NotificationCount.as_asgi())

]
