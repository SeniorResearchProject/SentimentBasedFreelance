from rest_framework import serializers
from .models import Employer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['id', 'name', 'user_id', 'comapanyName', 'comapanyUrl', 'email', 'logo', 'biography']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['location', 'phone']

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'