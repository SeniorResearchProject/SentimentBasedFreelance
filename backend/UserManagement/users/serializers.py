from rest_framework import serializers
from .models import User
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError



class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'username','email', 'password', 'confirm_password', 'is_employee', 'is_employer']
        extra_kwargs= {
            'password': {'write_only': True }
        }
    def validate(self, data):
        email= data.get('email', '')
        username= data.get('username', '')
        is_employee = data.get('is_employee', False)
        is_employer = data.get('is_employer', False)

        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric characters')
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("The passwords do not match.")
        return data
    

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password', None)
      
        # instance = self.Meta.model(**validated_data)
        instance = User.objects.create_user(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
class EmailVerificationSerializer(serializers.ModelSerializer):
    tokens = serializers.CharField(max_length=555, read_only=True)

    class Meta:
        model = User
        fields = ['tokens']

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=68, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    tokens = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model= User
        fields = ['email', 'password', 'username', 'tokens', 'role']


    # def validate(self, data):
    #     email = data.get('email', '')
    #     password = data.get('password', '')
    #     filtered_user_by_email = User.objects.filter(email=email)

    #     user = auth.authenticate(email=email, password=password)

    #     if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
    #         raise AuthenticationFailed(
    #             detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    #     if not user:
    #         raise AuthenticationFailed('Invalid credentials, try again')
    #     if not user.is_active:
    #         raise AuthenticationFailed('Account disabled, contact admin')
    #     if not user.is_verified:
    #         raise AuthenticationFailed('Email is not verified')
        
        
    #     if user.is_employee:
    #         role = 'employee'
    #     elif user.is_employer:
    #         role = 'employer'
        
        # return {
        #     'email': user.email,
        #     'username': user.username,
        #     'tokens':user.tokens,
        #     'role': role
        # }

        # return super().validate(data)


        
class ResetPasswordSerializer(serializers.Serializer):
    email= serializers.EmailField()

    class Meta:
        fields= ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields=['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password= attrs.get('password')
            token= attrs.get('token')
            uidb64= attrs.get('uidb64')

            id=force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)
            
            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        
        return super().validate(attrs)