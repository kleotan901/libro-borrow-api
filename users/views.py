from secrets import token_urlsafe

from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from telegram_notifications.models import Notification
from users.serializers import UserSerializer, UserListSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = get_user_model().objects.get(id=response.data["id"])
        connect_token = token_urlsafe(8)
        Notification.objects.create(user=user, connect_token=connect_token)
        return response


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserListSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
