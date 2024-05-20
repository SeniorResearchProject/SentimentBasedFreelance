from rest_framework import serializers
from . import google, facebook
from .register import register_social_user
import os
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import json


class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)

        try:
            user_id = user_data['id']
            email = user_data['email']
            name = user_data['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                user_id=user_id,
                email=email,
                name=name
            )
        except Exception as identifier:

            raise serializers.ValidationError(
                'The token  is invalid or expired. Please login again.'
            )

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        print(user_data)

        # Check if user_data is a string (JSON), parse it if necessary
        if isinstance(user_data, str):
            try:
                user_data = json.loads(user_data)
            except json.JSONDecodeError:
                raise serializers.ValidationError('The token is invalid or expired. Please login again.')

        # Check if the required user data fields are present
        try:
            user_id = user_data['id']
            email = user_data['email']
            name = user_data['name']
            provider = 'google'
        except KeyError:
            # If any required fields are missing, raise a validation error
            raise serializers.ValidationError('The token is invalid or expired. Please login again.')

        # Validate the audience (client ID) of the token
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('Oops, who are you?')

        # Register the user using the provided user data
        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name
        )