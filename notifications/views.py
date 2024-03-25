from rest_framework import views, response, status
from .models import NotificationModel
from .serializers import NotificationModelSerializers


class NotificationView(views.APIView):
    @staticmethod
    def get(request):
        user = request.user
        notification = (NotificationModel.objects.filter(notification_visible_to_user=user)
                        .order_by('-created_at').order_by('is_seen'))
        serializer_data = NotificationModelSerializers(notification, many=True)
        return response.Response(serializer_data.data, status=status.HTTP_200_OK)


class NotificationReadView(views.APIView):
    @staticmethod
    def get(request, notification_id):
        notification = NotificationModel.objects.get(id=notification_id)
        if not notification.is_seen:
            notification.is_seen = True
            notification.save()
        return response.Response(status=status.HTTP_200_OK)


class ReadAllNotificationsView(views.APIView):
    @staticmethod
    def get(request):
        user = request.user
        notifications = NotificationModel.objects.filter(notification_visible_to_user=user, is_seen=False)
        for notification in notifications:
            notification.is_seen = True
            notification.save()
        return response.Response(status=status.HTTP_200_OK)
