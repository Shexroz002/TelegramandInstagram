from .views import NotificationView, ReadAllNotificationsView, NotificationReadView
from django.urls import path

urlpatterns = [
    # this is the url for the notification
    path('', NotificationView.as_view(), name='notification'),
    # this is the url for the notification read
    path('read/<int:notification_id>/', NotificationReadView.as_view(), name='notification-read'),
    # this is the url for the notification read all
    path('read/all/', ReadAllNotificationsView.as_view(), name='notification-read-all'),
]
