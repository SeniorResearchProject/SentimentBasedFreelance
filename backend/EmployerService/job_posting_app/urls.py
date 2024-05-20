from django.urls import path
from .views import JobPostView,ViewFreelancers  # Make sure you're importing JobPostView correctly
from .views import ListAllJobs
from .views import ViewJob 
from .views import TaskSubmissionView
from .views import MilestoneProgressView
urlpatterns = [
    path('api/job-post/', JobPostView.as_view(), name='job_post'),
     path('api/viewfreelancers/', ViewFreelancers.as_view(), name='view-freelancers'),
    path('api/jobs/', ListAllJobs.as_view(), name='list-all-jobs'),
    path('api/jobs/<int:job_id>/', ViewJob.as_view(), name='view-job'),
    path('submit-task/', TaskSubmissionView.as_view(), name='submit-task'),
     path('jobs/<int:job_id>/milestones-progress/', MilestoneProgressView.as_view(), name='milestone-progress'),
]

