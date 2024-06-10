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
from django.shortcuts import get_object_or_404
# from .utils.token_decoder import extract_freelancer_id_from_token
from django.conf import settings
from requests import get
from .models import Job
from .serializers import JobSerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Job
from django.db.models import Count
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from rest_framework.permissions import AllowAny
from django.http import HttpResponse

def options_request_handler(request, *args, **kwargs):
    response = HttpResponse()
    response['Allow'] = 'GET, POST, OPTIONS, DELETE, PATCH, PUT'
    response['Access-Control-Allow-Origin'] = 'http://localhost:3001'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE, PATCH, PUT'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response
class JobPostView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()
        
        if user_info.get('user_id'):
            job_data = request.data
            job_data['posted_by_user_id'] = user_info['user_id']  # Assign the user ID to the posted_by field
            
            # Retrieve the list of employers
            employers_response = requests.get('http://localhost:8001/api/employer/list/')
            employers_list = employers_response.json()
            
            # Find the employer with the matching user_id
            employer_info = next((employer for employer in employers_list if employer['user_id'] == user_info['user_id']), None)
            
            if employer_info:
                job_data['comapanyName'] = employer_info['comapanyName']
                job_data['location'] = employer_info['location']

                serializer = JobSerializer(data=job_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Job posted successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Employer not found for the authenticated user.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
        
class JobListView(APIView):
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
        


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
            freelancer_id = freelancer.get('id')  # Adjusted to use 'freelancer_id' instead of 'id'
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
    def get(self, request, id):
        """ Retrieve specific job details """
        try:
            job = Job.objects.get(id=id)
            # Assuming you have a serializer for Job
            serializer = JobSerializer(job)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
class UpdateJobView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, id):
        try:
            job = Job.objects.get(id=id)
        except Job.DoesNotExist:
            return Response({"msg": "Job not found"}, status=404)

        # Extract only the fields you want to update
        update_data = {
            key: value for key, value in request.data.items()
            if key in ['title', 'description', 'location', 'salary', 'company_name']  # Add other fields if needed
        }

        serializer = JobSerializer(job, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)


class DeleteJobView(APIView):
    permission_classes = (AllowAny,)

    def delete(self, request, id):
        try:
            job = Job.objects.get(id=id)
        except Job.DoesNotExist:
            return Response({"msg": "Job not found"}, status=404)

        job.delete()
        return Response({'message': 'Job deleted successfully.'}, status=200)


    
from django.core.mail import send_mail
from rest_framework import views, status
from rest_framework.response import Response
# from .models import TaskSubmission
# from .serializers import TaskSubmissionSerializer

from rest_framework import views, status
from rest_framework.response import Response
from django.core.mail import send_mail
# from .serializers import TaskSubmissionSerializer

# class TaskSubmissionView(APIView):

#     def post(self, request, *args, **kwargs):
#         freelancer_id = extract_freelancer_id_from_token(request)
#         if freelancer_id is None:
#             return Response({"error": "Freelancer ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
#         # Retrieve the job application associated with the freelancer
#         job_application = get_object_or_404(JobApplication, freelancer_id=freelancer_id, application_status='accepted')
#         job_application_id = job_application.id
        
#         milestone = request.data.get('milestone')
#         task = request.data.get('task')
        
#         # Retrieve job ID from the JobApplication model
#         job_id = job_application.job_id
        
#         # Retrieve job details from the employer service using the job ID
#         employer_service_url = f'http://employer-service-url/jobs/{job_id}/'
#         response = requests.get(employer_service_url)
#         if response.status_code != 200:
#             return Response({"error": "Job not found in employer service"}, status=status.HTTP_404_NOT_FOUND)
        
#         job_data = response.json()
        
#         # Validate job
#         try:
#             job = Job.objects.get(pk=job_id)
#         except Job.DoesNotExist:
#             return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = TaskSubmissionSerializer(data=request.data)
#         if serializer.is_valid():
#             submission = serializer.save(freelancer_id=freelancer_id, job=job, milestone=milestone)
            
#             if 'file' in request.FILES:
#                 if request.FILES['file'].size > 10485760:  # Limit to 10 MB
#                     return Response({"message": "File too large, please use a link instead."}, status=status.HTTP_400_BAD_REQUEST)
#                 submission.file = request.FILES['file']
#             elif 'link' in request.data:
#                 submission.link = request.data['link']
#             else:
#                 return Response({"message": "Please submit either a file or a link."}, status=status.HTTP_400_BAD_REQUEST)
            
#             submission.save()
#             # Additional logic like sending emails, notifications, etc.
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.db.models import Max
from rest_framework import views, status
from rest_framework.response import Response
# from .models import Job, TaskSubmission
# from .serializers import TaskSubmissionSerializer

# class MilestoneProgressView(views.APIView):
#     def get(self, request, job_id):
#         try:
#             job = Job.objects.get(pk=job_id)
#             milestones = TaskSubmission.objects.filter(job=job).order_by('milestone').values('milestone').annotate(last_submission=Max('submission_date'))
#             detailed_submissions = []

#             for milestone in milestones:
#                 submissions = TaskSubmission.objects.filter(job=job, milestone=milestone['milestone'])
#                 serializer = TaskSubmissionSerializer(submissions, many=True)
#                 detailed_submissions.append({
#                     'milestone': milestone['milestone'],
#                     'last_submission': milestone['last_submission'],
#                     'submissions': serializer.data
#                 })

#             return Response(detailed_submissions)
#         except Job.DoesNotExist:
#             return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        
class JobCountByUserView(APIView):
    
    def get(self, request, posted_by_user_id):
        job_count = Job.objects.filter(posted_by_user_id=posted_by_user_id).count()
        return Response({'job_count': job_count}, status=status.HTTP_200_OK)
        
class JobListByUserView(APIView):
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if user_info.get('user_id'):
            user_id = user_info['user_id']
            jobs = Job.objects.filter(posted_by_user_id=user_id)
            serialized_data = JobSerializer(jobs, many=True).data
            return Response(serialized_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
    
class JobCountView(APIView):
    def get(self, request):
        job_count = Job.objects.count()
        return Response({'job_count': job_count}, status=status.HTTP_200_OK)
class UniqueCompanyCountView(APIView):
    def get(self, request):
        unique_company_count = Job.objects.values('company_name').distinct().count()
        return Response({'unique_company_count': unique_company_count}, status=status.HTTP_200_OK)
class RecentJobCountView(APIView):
    def get(self, request):
        days = int(request.query_params.get('days', 7))  # Default to last 7 days if not provided
        time_threshold = timezone.now() - timedelta(days=days)
        recent_job_count = Job.objects.filter(created_at__gte=time_threshold).count()
        return Response({'recent_job_count': recent_job_count}, status=status.HTTP_200_OK)


class JobStatisticsView(APIView):
    def get(self, request):
        total_jobs = Job.objects.count()
        jobs_by_location = Job.objects.values('location').annotate(count=Count('location'))
        jobs_by_company = Job.objects.values('comapanyName').annotate(count=Count('comapanyName'))
        avg_milestones = Job.objects.aggregate(Avg('milestones'))['milestones__avg']
        submissions_by_job = TaskSubmission.objects.values('job_id').annotate(count=Count('id'))
        
        statistics = {
            "total_jobs": total_jobs,
            "jobs_by_location": list(jobs_by_location),
            "jobs_by_company": list(jobs_by_company),
            "avg_milestones": avg_milestones,
            "submissions_by_job": list(submissions_by_job),
        }
        
        return Response(statistics)


class JobPostedTimeView(APIView):
    def get(self, request):
        # Fetch the count of jobs posted at different times
        job_posted_time = Job.objects.annotate(time=Count('id')).values('time', 'posted_at')

        # Format the time data
        data = [{'time': job['posted_at'].strftime('%Y-%m-%d %H:%M:%S'), 'job_count': job['time']} for job in job_posted_time]

        # Return the data as JSON response
        return Response(data)



# class GetSubmission(APIView):
#     authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]

#     def get(self, request):
#         token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers
#         user_info_response = requests.get(
#             f'{settings.USER_MANAGEMENT_URL}/api/token/validate/',
#             headers={'Authorization': token}
#         )
        
#         if user_info_response.status_code != 200:
#             return Response({'error': 'User authentication failed.'}, status=user_info_response.status_code)
        
#         user_info = user_info_response.json()
#         user_id = user_info.get('user_id')
        
#         if not user_id:
#             return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
        
#         jobs = Job.objects.filter(posted_by_user_id=user_id)
#         job_ids = jobs.values_list('id', flat=True)

#         submission_response = requests.get('http://localhost:8002/api/submissions/')
        
#         if submission_response.status_code != 200:
#             return Response({'error': 'Failed to fetch submissions from FreelancerMicroservice.'}, status=submission_response.status_code)
        
#         submission_list = submission_response.json()
#         employer_submissions = [submission for submission in submission_list if submission['job_id'] in job_ids]

#         return Response(employer_submissions, status=status.HTTP_200_OK)

                
