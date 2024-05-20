from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from requests import get
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from requests import get
from .models import Job
from .serializers import JobSerializer


class JobPostView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()
        
        if user_info.get('user_id'):
            job_data = request.data
            job_data['posted_by_user_id'] = user_info['user_id']  # Assign the user ID to the posted_by field
            serializer = JobSerializer(data=job_data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Job posted successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)



class ViewFreelancers(APIView):
    def get(self, request):
        # URL for the Freelancer Service
        freelancer_url = 'http://localhost:8002/api/freelancers/'
        sentiment_base_url = 'http://localhost:8003/api/sentiment/'

        try:
            # Get freelancers from the Freelancer Service
            freelancers_response = requests.get(freelancer_url)
            freelancers_response.raise_for_status()  # Ensure we raise exceptions on bad status
            freelancers = freelancers_response.json()
            if not freelancers:
                return Response({"message": "No freelancers found."}, status=status.HTTP_204_NO_CONTENT)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Could not retrieve freelancers due to: " + str(e)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Process each freelancer to fetch their sentiment data
        for freelancer in freelancers:
            freelancer_id = freelancer.get('freelancer_id')  # Adjusted to use 'freelancer_id' instead of 'id'
            if not freelancer_id:
                print("Freelancer ID missing in data:", freelancer)  # Log for debugging
                freelancer['sentiment'] = {'error': 'Freelancer ID missing'}
            else:
                try:
                    # Construct URL for each freelancer's sentiment
                    sentiment_url = f'{sentiment_base_url}{freelancer_id}/'
                    sentiment_response = requests.get(sentiment_url)
                    sentiment_response.raise_for_status()  # Ensures HTTP errors raise an exception
                    freelancer['sentiment'] = sentiment_response.json()  # Assign sentiment data
                except requests.exceptions.RequestException:
                    # Log this issue or handle it as needed
                    freelancer['sentiment'] = {'error': 'Sentiment data unavailable'}

        # Return the modified list of freelancers with sentiment data added
        return Response(freelancers)
        
class ViewJob(APIView):
    def get(self, request, job_id):
        """ Retrieve specific job details """
        try:
            job = Job.objects.get(id=job_id)
            # Assuming you have a serializer for Job
            serializer = JobSerializer(job)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class ListAllJobs(APIView):
    def get(self, request):
        """ List all jobs """
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
from django.core.mail import send_mail
from rest_framework import views, status
from rest_framework.response import Response
from .models import TaskSubmission
from .serializers import TaskSubmissionSerializer

from rest_framework import views, status
from rest_framework.response import Response
from django.core.mail import send_mail
from .serializers import TaskSubmissionSerializer

class TaskSubmissionView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = TaskSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            submission = serializer.save()
            
            # Check if a file is included and process it
            if 'file' in request.FILES:
                if request.FILES['file'].size > 10485760:  # Limit to 10 MB
                    return Response({"message": "File too large, please use a link instead."}, status=status.HTTP_400_BAD_REQUEST)
                submission.file = request.FILES['file']
            
            # Check if a link is included and process it
            elif 'link' in request.data:
                submission.link = request.data['link']
            else:
                return Response({"message": "Please submit either a file or a link."}, status=status.HTTP_400_BAD_REQUEST)

            submission.save()

            # Send email notification
            send_mail(
                'New Task Submission',
                f'A new task has been submitted for job {submission.job.title}, milestone {submission.milestone}.',
                'from@example.com',
                ['to@example.com'],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.db.models import Max
from rest_framework import views, status
from rest_framework.response import Response
from .models import Job, TaskSubmission
from .serializers import TaskSubmissionSerializer

class MilestoneProgressView(views.APIView):
    def get(self, request, job_id):
        try:
            job = Job.objects.get(pk=job_id)
            milestones = TaskSubmission.objects.filter(job=job).order_by('milestone').values('milestone').annotate(last_submission=Max('submission_date'))
            detailed_submissions = []

            for milestone in milestones:
                submissions = TaskSubmission.objects.filter(job=job, milestone=milestone['milestone'])
                serializer = TaskSubmissionSerializer(submissions, many=True)
                detailed_submissions.append({
                    'milestone': milestone['milestone'],
                    'last_submission': milestone['last_submission'],
                    'submissions': serializer.data
                })

            return Response(detailed_submissions)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
