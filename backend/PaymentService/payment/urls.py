# from django.urls import path
# from .views import InitializeTransaction, VerifyTransaction

# urlpatterns = [
#     path('initialize/', InitializeTransaction.as_view(), name='initialize-transaction'),
#     path('verify/<str:tx_ref>/', VerifyTransaction.as_view(), name='verify-transaction'),
# ]

from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('initialize/', views.payment_initialize, name='payment_initialize'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('total-revenue/', views.RevenueView, name='revenue'),
    path('transactions/', views.TransactionsView, name='transactions'),
    path('average-value/', views.AverageValueView, name='average_value'),
]
