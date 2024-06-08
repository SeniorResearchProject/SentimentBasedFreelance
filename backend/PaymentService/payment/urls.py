# from django.urls import path
# from .views import InitializeTransaction, VerifyTransaction

# urlpatterns = [
#     path('initialize/', InitializeTransaction.as_view(), name='initialize-transaction'),
#     path('verify/<str:tx_ref>/', VerifyTransaction.as_view(), name='verify-transaction'),
# ]

from django.urls import path
from django.urls import path
from .views import payment_initialize, payment_callback, get_csrf_token,RevenueView,TransactionsView,AverageValueView
app_name = 'payment'

urlpatterns = [
    path('initialize/', payment_initialize, name='payment_initialize'),
    path('callback/', payment_callback, name='payment_callback'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('total-revenue/', views.RevenueView.as_view(), name='revene'),
	path('transactions/', views.TransactionsView.as_view(), name='transactions'),
	path('average-value/', views.AverageValueView.as_view(), name='average value'),
]