from django.urls import path
from .views import AccountView, CompanyView, EmployerView, EmployerListView

urlpatterns = [
    path('employer/company/', CompanyView.as_view(), name='employer-company'),
    path('employer/account/', AccountView.as_view(), name='employer-account'),
    path('employer/<int:id>/', EmployerView.as_view(), name='employer-info'),
    path('employer/list/', EmployerListView.as_view(), name='employer-list'),

]