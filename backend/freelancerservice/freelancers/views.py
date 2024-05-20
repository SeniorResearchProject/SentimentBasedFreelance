from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Freelancer
from .serializers import FreelancerSerializer
import requests
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from .models import JobApplication
from .serializers import JobApplicationSerializer
from rest_framework import status
class FreelancerListView(APIView):
    def get(self, request):
        freelancers = Freelancer.objects.all()
        serializer = FreelancerSerializer(freelancers, many=True)
        return Response(serializer.data)

class ExternalJobListView(APIView):
    def get(self, request):
        """ Retrieves all jobs from the Employer service """
        response = requests.get(f'http://localhost:8001/api/jobs/')
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to retrieve jobs'}, status=response.status_code)

class ExternalJobDetailView(APIView):
    def get(self, request, job_id):
        """ Retrieves a specific job from the Employer service """
        response = requests.get(f'http://localhost:8001/api/jobs/{job_id}/')
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to retrieve job'}, status=response.status_code)


class ApplyForJobView(APIView):
    def post(self, request):
        serializer = JobApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicationDecisionView(APIView):
    def patch(self, request, application_id):
        application = JobApplication.objects.get(pk=application_id)
        serializer = JobApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
