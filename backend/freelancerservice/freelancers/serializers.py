from rest_framework import serializers
from .models import Freelancer
from .models import JobApplication
from .models import TaskSubmission

class BasicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields = ['id', 'name', 'user_id', 'experience', 'education_level', 'website', 'photo', 'cv', 'email']

class SecondProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields = ['Nationality', 'gender', 'profession', 'date_of_birth', 'biography']

class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields = ['salary_range', 'employeeType']



class FreelancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields = '__all__'



class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['application_status']

class TaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubmission
        fields = '__all__'




