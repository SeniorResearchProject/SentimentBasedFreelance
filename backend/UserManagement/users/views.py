from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.messages import constants as messages_constants
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer, ResetPasswordSerializer, SetNewPasswordSerializer
from rest_framework_simplejwt.tokens import AccessToken
from .models import User
from .utils import Util
import jwt, datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import logging

logger = logging.getLogger(__name__)


# Create your views here.

class RegisterView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_data= serializer.data
            user=User.objects.get(email=  user_data['email'])

            token = jwt.encode({'id': user.id}, 'secret', algorithm='HS256')

            current_site= get_current_site(request).domain
            relativeLink= reverse('email-verify')
            absurl='http://'+current_site+relativeLink+"?token="+str(token)
            email_body = 'Hi '+user.username+' Use link below to verify your email \n'+ absurl
            
            data= {'email_body':email_body, 'email_subject': 'Verify your email', 'to_email':user.email}
            
            Util.send_email(data)

            return Response( user_data,status=status.HTTP_201_CREATED)
            # return redirect('login')
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmail(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        token = request.GET.get('token')  # Extract token from request URL
        if not token:
            return Response({'error': 'Token is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])  # Decode token
            user = User.objects.filter(id=payload['id']).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
                
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)  # Redirect to success page or return a success message

            return Response({'message': 'Email already verified'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

   
class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Login endpoint",
        request_body=LoginSerializer,
        responses={200: openapi.Response('JWT Token', LoginSerializer)}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        
        try:
            user = User.objects.get(email=user_data['email'])
            if not user.is_active:
                raise AuthenticationFailed('Account disabled, contact admin')
            if not user.is_verified:
                raise AuthenticationFailed('Email is not verified')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found!')

        # Generate tokens using django-rest-framework-simplejwt
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        if user.is_employee:
            role = 'employee'
        elif user.is_employer:
            role = 'employer'
        elif user.is_staff:
            role = 'admin'

        response = Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'role': role
        }, status=status.HTTP_200_OK)

        # Set cookies for the tokens; HTTP Only for security
        response.set_cookie(key='refresh_token', value=str(refresh), httponly=True)
        response.set_cookie(key='access_token', value=str(access_token), httponly=True)

        # Also include JWT in the response headers
        response['Authorization'] = f'Bearer {str(access_token)}'
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        response = Response()
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.data = {
            'message': 'successefully logged out'
        }
        return response
    


  
class AllUsersView(APIView):
    permission_classes = (IsAdminUser,)
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
  
class UpdateUserView(APIView):
    permission_classes = (IsAdminUser,)
    @login_required(login_url='login') 
    def put(self, request, id):
        try:
            user = User.objects.get(id=id)

        except User.DoesNotExist:
            msg= {"msg": "not found error"}
            return Response(msg, status=404)
    
    # Assuming you have a UserSerializer to handle user data
        serializer = UserSerializer(user, data=request.POST or request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=205)
    
        return Response(serializer.errors, status=400) 

  
class DeleteUserView(APIView):
    permission_classes = (IsAdminUser,)
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)

        except User.DoesNotExist:
            msg= {"msg": "not found error"}
            return Response(msg, status=404)
        
        user.delete()
        return Response({'message': 'User deleted successfully.'})


class RequestPasswordResetEmail(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class=ResetPasswordSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']
        if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site= get_current_site(request=request).domain
                relativeLink= reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token':token})
                absurl='http://'+current_site + relativeLink
                email_body = 'Hello, \n Use link below to reset your password \n'+ absurl
                
                data= {'email_body':email_body, 'email_subject': 'Reset your password', 'to_email':user.email}
                
                Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        
        except DjangoUnicodeDecodeError as e:
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
        

class SetNewPasswordView(generics.GenericAPIView):
    serializer_class= SetNewPasswordSerializer

    def patch(self, request):
           serializer=self.serializer_class(data=request.data)   
           serializer.is_valid(raise_exception=True)
           return Response({'success':True, 'message':'Password reset sucess'}, status=status.HTTP_200_OK)



class ValidateTokenView(APIView):
    # permission_classes = [IsAuthenticated]

    permission_classes = [IsAuthenticated]  

    def get(self, request, *args, **kwargs):
        
        user = request.user
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'name': user.name,
            'email' : user.email,
        })

    
