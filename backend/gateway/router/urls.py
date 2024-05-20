from django.urls import path, re_path
from .views import ProxyAPIView

urlpatterns = [
    re_path(r'^(?P<path>.*)$', ProxyAPIView.as_view()),
]
