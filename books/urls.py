from rest_framework import routers

from books.views import BookViewSet

from django.urls import path, include

app_name = "books"

router = routers.DefaultRouter()
router.register("", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
