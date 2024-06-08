from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Employer
import requests
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from .serializers import CompanySerializer, AccountSerializer, EmployerSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.shortcuts import get_object_or_404

class CompanyView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            email = user_info['email']
            name = user_info['name']

            employer, created = Employer.objects.get_or_create(user_id=user_id, email=email, name=name)
            serializer = CompanySerializer(employer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Basic Profile Set successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)


class AccountView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            employer = get_object_or_404(Employer, user_id=user_id)
            serializer = AccountSerializer(employer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Account added successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)


class EmployerListView(APIView):
    def get(self, request):
        employers = Employer.objects.all()
        serializer = EmployerSerializer(employers, many=True)
        return Response(serializer.data)
    
class EmployerView(APIView): 
    def get(self, request, id):
        try:
            employer = Employer.objects.get(id=id)
        except Employer.DoesNotExist:
            msg = {"msg": "not found error"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployerSerializer(employer)
        return Response(serializer.data, status=status.HTTP_200_OK)
