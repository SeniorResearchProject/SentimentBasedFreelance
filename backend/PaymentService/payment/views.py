from django.shortcuts import render
from django.http import HttpResponse
from .models import Transaction
from .forms import PaymentForm
from .utils import create_payload, get_chapa_token, get_secret_key
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
import logging
from .serializers import TransactionSerializer
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from django.db.models.functions import ExtractMonth
from .models import Transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Transaction

logger = logging.getLogger(__name__)

@csrf_exempt
def payment_initialize(request):
    if request.method == 'POST':
        authentication_classes = [TokenAuthentication]
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        
        if not token:
            return JsonResponse({'error': 'Authorization token missing'}, status=401)
        
        # Validate token and get user information from the UserManagement microservice
        try:
            user_info_response = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token})
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
        except requests.RequestException as e:
            logger.error(f'Error validating token: {e}')
            return JsonResponse({'error': 'Invalid token or unable to validate token'}, status=401)
        
        if not user_info.get('user_id'):
            return JsonResponse({'error': 'User information not found in token'}, status=401)

        if request.method == 'POST':
            data = json.loads(request.body)
            serializer = TransactionSerializer(data={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'amount': data['amount'],
                'tx_ref': data['tx_ref'],
                'status': 'created',
                'employer': user_info['user_id']
            })

        if serializer.is_valid():
            transaction = serializer.save()

            chapa_payload = {
                "amount": data['amount'],
                "currency": "ETB",
                "email": data['email'],
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "phone_number": data.get('phone_number', ''),
                "tx_ref": data['tx_ref'],
                "callback_url": data.get('callback_url', 'http://localhost:8004/payment/callback/'),
                "return_url": data.get('return_url', 'http://localhost:3000/thanks'),
                "customization": {
                    "title": data.get('title', 'Let us do this'),
                    "description": data.get('description', 'Paying with Confidence with Chapa')
                }
            }

            chapa_headers = {
                'Authorization': 'Bearer CHASECK_TEST-32Cwztibxuk2GEm8lU6cQxWaitxmv9T4',  # Replace with your actual secret key
                'Content-Type': 'application/json'
            }

            chapa_url = 'https://api.chapa.co/v1/transaction/initialize'

            chapa_response = requests.post(chapa_url, json=chapa_payload, headers=chapa_headers)
            chapa_data = chapa_response.json()

            if chapa_response.status_code == 200 and chapa_data.get('status') == 'success':
                redirect_url = chapa_data['data']['checkout_url']
                return JsonResponse({'redirect_url': redirect_url})

            return JsonResponse({'error': 'Error initializing payment with Chapa'}, status=400)

        return JsonResponse(serializer.errors, status=400)

    return HttpResponse('Method not allowed', status=405)
@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        tx_ref = request.POST.get('trx_ref')  # Corrected parameter name
        status = request.POST.get('status')
    elif request.method == 'GET':
        tx_ref = request.GET.get('trx_ref')  # Corrected parameter name
        status = request.GET.get('status')
    else:
        return HttpResponse('Invalid request method', status=405)

    logger.debug(f'Received callback with trx_ref: {tx_ref} and status: {status}')

    if not tx_ref or not status:
        return HttpResponse('Missing trx_ref or status', status=400)

    try:
        transaction = Transaction.objects.get(tx_ref=tx_ref)
        logger.debug(f'Transaction found: {transaction}')
    except Transaction.DoesNotExist:
        logger.error(f'Transaction not found for trx_ref: {tx_ref}')
        return HttpResponse('Transaction not found', status=404)

    # Verify payment with Chapa
    chapa_verify_url = f'https://api.chapa.co/v1/transaction/verify/{tx_ref}'
    chapa_headers = {
        'Authorization': 'Bearer CHASECK_TEST-32Cwztibxuk2GEm8lU6cQxWaitxmv9T4',  # Replace with your actual secret key
    }

    try:
        chapa_response = requests.get(chapa_verify_url, headers=chapa_headers)
        chapa_response.raise_for_status()
        chapa_data = chapa_response.json()

        if chapa_data.get('status') == 'success' and chapa_data['data']['status'] == 'success':
            if transaction.status == 'created':
                transaction.status = 'completed'
                transaction.save()
                return HttpResponse('Payment successful')
            else:
                return HttpResponse('Payment already processed')
        else:
            return HttpResponse('Payment verification failed', status=400)
    except requests.exceptions.RequestException as e:
        logger.error(f'Error verifying payment with Chapa: {e}')
        return HttpResponse('Error verifying payment', status=500)
    
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

class RevenueView(APIView):
    def get(self, request):
        # Get the current year
        current_year = timezone.now().year
        
        # Query total revenue from Transaction objects where status is 'completed' and created_at is within the current year
        revenue_by_month = Transaction.objects.filter(status='completed', created_at__year=current_year).annotate(month=ExtractMonth('created_at')).values('month').annotate(revenue=Sum('amount')).order_by('month')

        # Constructing the dataset in the format expected by the frontend
        dataset = [
            {'month': calendar.month_abbr[month['month']], 'revenue': month['revenue'] or 0} for month in revenue_by_month
        ]

        # Returning the dataset as a response
        return Response({"revenue_data": dataset})



class TransactionsView(APIView):
    def get(self, request):
        current_year = timezone.now().year
        transactions_of_year = Transaction.objects.filter(created_at__year=current_year)
        
        # Constructing the dataset with payment time and amount
        transactions_data = [
            {'payment_time': transaction.created_at, 'payment_amount': transaction.amount} 
            for transaction in transactions_of_year
        ]
        
        return Response({"transactions": transactions_data})


class AverageValueView(APIView):
    def get(self, request):
        # Annotate average transaction amount per month
        average_values = Transaction.objects.annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(
            average_transaction=Avg('amount')
        ).order_by('month')

        # Constructing the dataset in the format expected by the frontend
        data = [
            {'month': calendar.month_abbr[item['month']], 'average_transaction': item['average_transaction']}
            for item in average_values
        ]

        # Return the JSON response
        return Response({"average_values": data})
