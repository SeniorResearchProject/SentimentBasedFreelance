from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Freelancer
from .serializers import FreelancerSerializer
import requests
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from .models import JobApplication, TaskSubmission
from .serializers import JobApplicationSerializer, BasicProfileSerializer, SecondProfileSerializer, AdressSerializer, StatusSerializer, TaskSubmissionSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from django.core.files.base import ContentFile
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import JobApplication
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Freelancer, JobApplication

class BasicView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            email = user_info['email']
            name = user_info['name']

            freelancer, created = Freelancer.objects.get_or_create(user_id=user_id, email=email, name=name)
            serializer = BasicProfileSerializer(freelancer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Basic Profile Set successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

class SecondProfileView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            freelancer = get_object_or_404(Freelancer, user_id=user_id)
            serializer = SecondProfileSerializer(freelancer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Second Profile Set successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

class AdressView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            freelancer = get_object_or_404(Freelancer, user_id=user_id)
            serializer = AdressSerializer(freelancer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Address added successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

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
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(
            f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', 
            headers={'Authorization': token}
        ).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            job_id = request.data.get('job_id')  # Ensure job_id is obtained from the frontend

            if not job_id:
                return Response({'error': 'Job ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                job_id = int(job_id)
            except ValueError:
                return Response({'error': 'Invalid job ID format.'}, status=status.HTTP_400_BAD_REQUEST)

            job_response = requests.get('http://localhost:8001/api/job-list/')
            if job_response.status_code != 200:
                return Response({'error': 'Failed to fetch job list.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            job_list = job_response.json()
            job_info = next((job for job in job_list if job['id'] == job_id), None)

            if not job_info:
                return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

            try:
                freelancer = Freelancer.objects.get(user_id=user_id)
            except Freelancer.DoesNotExist:
                return Response({'error': 'Freelancer not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Add job title and freelancer name to request data
            request.data['job_title'] = job_info['title']
            request.data['freelancer_name'] = freelancer.name
            request.data['freelancer'] = user_id  # Assigning freelancer directly using user_id
            request.data['milestone'] = job_info['milestones']

            serializer = JobApplicationSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
        
class FreelancerJobApplicationsView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()
       

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            applications = JobApplication.objects.filter(freelancer=user_id)
            serializer = JobApplicationSerializer(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

class FreelancerAcceptedView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()
       

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            applications = JobApplication.objects.filter(freelancer=user_id, application_status='accepted')
            serializer = JobApplicationSerializer(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

class EmployerJobApplicationsView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(
            f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', 
            headers={'Authorization': token}
        ).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            
            job_response = requests.get('http://localhost:8001/api/job-list/')
            if job_response.status_code == 200:
                job_list = job_response.json()
                user_jobs = [job['id'] for job in job_list if job['posted_by_user_id'] == user_id]
                
                if not user_jobs:
                    return Response({'error': 'No jobs posted by this user found.'}, status=status.HTTP_404_NOT_FOUND)

                job_applications = JobApplication.objects.filter(job_id__in=user_jobs,application_status='pending')
                serializer = JobApplicationSerializer(job_applications, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to fetch job list.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
        
class ViewFreelancer(APIView):
    def get(self, request, id):
        """ Retrieve specific job details """
        try:
            freelancer = Freelancer.objects.get(id=id)
            # Assuming you have a serializer for Job
            serializer = FreelancerSerializer(freelancer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Freelancer.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        
class ApplicationDecisionView(APIView):
    def patch(self, request, application_id):
        application = JobApplication.objects.get(pk=application_id)
        serializer = JobApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class FreelancerCountView(APIView):
    def get(self, request):
        freelancer_count = Freelancer.objects.count()
        return Response({'freelancer_count': freelancer_count}, status=status.HTTP_200_OK)
    
class AcceptFreelancerView(APIView):
    def put(self, request, id):
        try:
            freelancer_application = JobApplication.objects.get(id=id)
        except JobApplication.DoesNotExist:
            msg = {"msg": "Not found error"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        # Update the application_status field to 'accepted'
        data = {'application_status': 'accepted'}
        serializer = StatusSerializer(freelancer_application, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeclineFreelancerView(APIView):
    def put(self, request, id):
        try:
            freelancer_application = JobApplication.objects.get(id=id)
        except JobApplication.DoesNotExist:
            msg = {"msg": "Not found error"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        # Update the application_status field to 'declined'
        data = {'application_status': 'declined'}
        serializer = StatusSerializer(freelancer_application, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AcceptedApplicationView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(
            f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', 
            headers={'Authorization': token}
        ).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            
            job_response = requests.get('http://localhost:8001/api/job-list/')
            if job_response.status_code == 200:
                job_list = job_response.json()
                user_jobs = [job['id'] for job in job_list if job['posted_by_user_id'] == user_id]
                
                if not user_jobs:
                    return Response({'error': 'No jobs posted by this user found.'}, status=status.HTTP_404_NOT_FOUND)

                job_applications = JobApplication.objects.filter(job_id__in=user_jobs, application_status='accepted')
                serializer = JobApplicationSerializer(job_applications, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to fetch job list.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

class ApplicationView(APIView):
    def get(self, request, id):
        """ Retrieve specific job details """
        try:
            applications = JobApplication.objects.get(id=id)
            # Assuming you have a serializer for Job
            serializer = JobApplicationSerializer(applications)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

class MilestoneView(APIView):
    def get(self, request, id):
        """ Retrieve specific job details """
        try:
            application = JobApplication.objects.get(id=id)
            milestone_data = {'milestone': application.milestone}
            return Response(milestone_data, status=status.HTTP_200_OK)
        except JobApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        
class ApplicationListView(APIView):
    def get(self, request):
        applications = JobApplication.objects.all()
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
        

class TaskSubmissionView(APIView):
    authentication_classes = [TokenAuthentication]
    parser_classes = [JSONParser]  # Ensure the parser can handle JSON data

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(
            f'{settings.USER_MANAGEMENT_URL}/api/token/validate/',
            headers={'Authorization': token}
        ).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            job_application_id = request.data.get('job_applied')  # Ensure the job application ID is obtained from the frontend

            if not job_application_id:
                return Response({'error': 'Job Application ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                job_application_id = int(job_application_id)
            except ValueError:
                return Response({'error': 'Invalid Job Application ID format.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                job_application = JobApplication.objects.get(id=job_application_id)
            except JobApplication.DoesNotExist:
                return Response({'error': 'Job Application not found.'}, status=status.HTTP_404_NOT_FOUND)

            job_id = job_application.job_id

            job_response = requests.get('http://localhost:8001/api/job-list/')
            if job_response.status_code != 200:
                return Response({'error': 'Failed to fetch job list.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            job_list = job_response.json()
            job_info = next((job for job in job_list if job['id'] == job_id), None)

            if not job_info:
                return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data for TaskSubmission
            file_data = request.data.get('file')
            file = None
            if file_data:
                format, file_str = file_data.split(';base64,')
                ext = format.split('/')[-1]
                file = ContentFile(base64.b64decode(file_str), name=f'submission.{ext}')

            task_submission_data = {
                'freelancer': job_application.freelancer,
                'freelancer_name': job_application.freelancer_name,
                'job_id': job_application.job_id,
                'job_title': job_application.job_title,
                'milestone': job_info.get('milestones'),
                'submission_date': request.data.get('submission_date'),
                'file': file,
                'link': request.data.get('link'),
                'job_applied': job_application_id  # Add the job_applied field
            }

            serializer = TaskSubmissionSerializer(data=task_submission_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
class SubmissionsListView(APIView):
    def get(self, request):
        submissions = TaskSubmission.objects.all()
        serializer = TaskSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)
        

class GetSubmission(APIView):
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(
            f'{settings.USER_MANAGEMENT_URL}/api/token/validate/',
            headers={'Authorization': token}
        ).json()
        
        if user_info.get('user_id'):
            user_id = user_info['user_id']
            
            job_response = requests.get('http://localhost:8001/api/job-list/')
            if job_response.status_code == 200:
                job_list = job_response.json()
                user_jobs = [job['id'] for job in job_list if job['posted_by_user_id'] == user_id]
                
                if not user_jobs:
                    return Response({'error': 'No jobs posted by this user found.'}, status=status.HTTP_404_NOT_FOUND)

                job_submissions = TaskSubmission.objects.filter(job_id__in=user_jobs)
                serializer = TaskSubmissionSerializer(job_submissions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to fetch job list.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
        
class TaskByIdView(APIView):
    def get(self, request, task_id):
        try:
            task = TaskSubmission.objects.get(id=task_id)
            serializer = TaskSubmissionSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TaskSubmission.DoesNotExist:
            return Response({'error': 'submission not found'}, status=status.HTTP_404_NOT_FOUND)
        

class FreelancerRatingView(APIView):
    def get(self, request, freelancer_id):
        # Construct the URL to the Sentiment microservice
        sentiment_url = f'http://localhost:8003/api/sentiment/{freelancer_id}/'
        
        # Fetch sentiment data from the Sentiment microservice
        sentiment_response = requests.get(sentiment_url)
        
        if sentiment_response.status_code != 200:
            return Response({'error': 'Failed to fetch sentiment data.'}, status=sentiment_response.status_code)

        try:
            sentiment_data = sentiment_response.json()
        except requests.exceptions.JSONDecodeError as e:
            return Response({'error': 'Invalid response format from sentiment service.'}, status=500)

        # Ensure the sentiment_data contains the required fields
        if 'freelancer_id' not in sentiment_data or 'average_rate' not in sentiment_data:
            return Response({'error': 'Incomplete data from sentiment service.'}, status=500)

        # Fetch the freelancer object
        freelancer_object = Freelancer.objects.filter(user_id=freelancer_id)

        if not freelancer_object.exists():
            return Response({'error': 'Freelancer not found.'}, status=404)

        # Update the freelancer's rate with the average rate from the sentiment data
        average_rate = sentiment_data['average_rate']
        freelancer_object.update(rate=average_rate)

        return Response({
            'message': 'Freelancer rate updated successfully',
            'freelancer_id': freelancer_id,
            'average_rate': average_rate
        }, status=200)
      
class FreelancerStatisticsView(APIView):
    def get(self, request):
        total_freelancers = Freelancer.objects.count()
        available_freelancers = Freelancer.objects.filter(available=True).count()
        avg_experience = Freelancer.objects.aggregate(Avg('experience'))['experience__avg']
        application_status_counts = JobApplication.objects.values('application_status').annotate(count=Count('application_status'))
        
        statistics = {
            "total_freelancers": total_freelancers,
            "available_freelancers": available_freelancers,
            "avg_experience": avg_experience,
            "application_status_counts": list(application_status_counts),
        }
        
        return Response(statistics)



class JobApplicationStatusView(APIView):
    def get(self, request):
        # Query the database to get the count of job applications with different statuses
        pending_count = JobApplication.objects.filter(application_status='pending').count()
        accepted_count = JobApplication.objects.filter(application_status='accepted').count()
        declined_count = JobApplication.objects.filter(application_status='declined').count()

        # Structure the data into the format expected by the pie chart component
        data = [
            {'label': 'Pending', 'value': pending_count},
            {'label': 'Accepted', 'value': accepted_count},
            {'label': 'Declined', 'value': declined_count},
        ]

        # Return the structured data as a JSON response
        return Response(data)

                

        