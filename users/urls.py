from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import ManageUserView, CreateUserView, CustomTokenObtain

app_name = "users"

urlpatterns = [
    path("", CreateUserView.as_view(), name="create"),
    path("token/", CustomTokenObtain.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", ManageUserView.as_view(), name="manage"),
]
