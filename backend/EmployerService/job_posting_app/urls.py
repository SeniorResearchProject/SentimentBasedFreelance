from django.urls import path
from .views import JobPostView,ViewFreelancers,UpdateJobView, DeleteJobView,JobStatisticsView,JobPostedTimeView, JobListView, JobCountView, UniqueCompanyCountView, RecentJobCountView, JobCountByUserView, JobListByUserView# Make sure you're importing JobPostView correctly
from .views import ViewJob 
# from .views import TaskSubmissionView
# from .views import MilestoneProgressView
from django.urls import re_path
from .views import options_request_handler


urlpatterns = [
    re_path(r'^api/.*$', options_request_handler),
    path('job-post/', JobPostView.as_view(), name='job_post'),
    path('job-list/', JobListView.as_view(), name='job_list'),
    path('viewfreelancers/', ViewFreelancers.as_view(), name='view-freelancers'),
    path('jobs/<int:id>/', ViewJob.as_view(), name='view-job'),
    # path('submit-task/', TaskSubmissionView.as_view(), name='submit-task'),
    # path('jobs/<int:job_id>/milestones-progress/', MilestoneProgressView.as_view(), name='milestone-progress'),
    path('api/jobs/<int:id>/update/', UpdateJobView.as_view(), name='update-job'),
    path('api/jobs/<int:id>/delete/', DeleteJobView.as_view(), name='delete-job'),
    path('job-count/', JobCountView.as_view(), name='job-count'),
     path('unique-company-count/', UniqueCompanyCountView.as_view(), name='unique-company-count'),
     path('recent-job-count/', RecentJobCountView.as_view(), name='recent-job-count'),
     path('job-count-by-user/<int:posted_by_user_id>/', JobCountByUserView.as_view(), name='job-count-by-user'),
    path('job-list-by-user/', JobListByUserView.as_view(), name='job-list-by-user'),
    # path('jobs/<int:job_id>/', JobDetailView.as_view(), name='job-detail'),
     path('api/job-statistics/', JobStatisticsView.as_view(), name='job-statistics'),
     path('api/job-posted-time/', JobPostedTimeView.as_view(), name='job-posted-time'),
]

