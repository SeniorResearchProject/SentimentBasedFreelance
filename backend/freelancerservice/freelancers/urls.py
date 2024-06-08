from django.urls import path
from .views import FreelancerListView,ExternalJobListView,FreelancerStatisticsView,JobApplicationStatusView,ExternalJobDetailView,ApplyForJobView, ApplicationDecisionView, BasicView, SecondProfileView, AdressView, FreelancerCountView, FreelancerJobApplicationsView, ViewFreelancer, EmployerJobApplicationsView, AcceptFreelancerView, DeclineFreelancerView, AcceptedApplicationView , TaskSubmissionView, ApplicationView,  ApplicationListView, SubmissionsListView, GetSubmission, TaskByIdView, FreelancerAcceptedView, MilestoneView, FreelancerRatingView

urlpatterns = [
    path('freelancer/post1/', BasicView.as_view(), name='freelancer-post1'),
    path('freelancer/post2/', SecondProfileView.as_view(), name='freelancer-post2'),
    path('freelancer/post3/', AdressView.as_view(), name='freelancer-post3'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancer-list'),
    path('job-application/<int:id>/', ApplicationView.as_view(), name='job-application'),
    path('milestone/<int:id>/', MilestoneView.as_view(), name='milestone'),
    path('job-applications/', ApplicationListView.as_view(), name='job-application-list'),
    path('get-submission/', GetSubmission.as_view(), name='get-submission'),
    path('get-submission/<int:task_id>/', TaskByIdView.as_view(), name='task-submitted'),
    path('submissions/', SubmissionsListView.as_view(), name='submission-list'),
    path('freelancers/employer/', EmployerJobApplicationsView.as_view(), name='freelancer-list'),
    path('freelancers/<int:id>/', ViewFreelancer.as_view(), name='view-freelancer'),
    path('freelancer-rating/<int:freelancer_id>/', FreelancerRatingView.as_view(), name='view-freelancer'),
    path('viewjobs/', ExternalJobListView.as_view(), name='external-job-list'),
    path('viewajob/<int:job_id>/', ExternalJobDetailView.as_view(), name='external-job-detail'),
    path('apply/', ApplyForJobView.as_view(), name='apply-for-job'),
    path('submit-task/', TaskSubmissionView.as_view(), name='submit-task'),
    path('applications/<int:application_id>/', ApplicationDecisionView.as_view(), name='application-decision'),
    path('freelancer-count/', FreelancerCountView.as_view(), name='freelancer-count'),
    path('accept-freelancer/<int:id>/', AcceptFreelancerView.as_view()),
    path('decline-freelancer/<int:id>/', DeclineFreelancerView.as_view()),
    path('freelancer-job-applications/', FreelancerJobApplicationsView.as_view(), name='freelancer-job-applications'),
    path('freelancer-accepted-applications/', FreelancerAcceptedView.as_view(), name='freelancer-job-applications'),
    path('accepted-applications/', AcceptedApplicationView.as_view(), name='accepted-applications'),
    # path('milestones/<int:job_application_id>/', MilestoneDetailView.as_view(), name='milestone-detail'),
    path('freelancer-statistics/', FreelancerStatisticsView.as_view(), name='freelancer-statistics'),
    path('task-status/', JobApplicationStatusView.as_view(), name='task-status'),

]

