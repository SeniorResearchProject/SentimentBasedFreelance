from django.urls import path
from .views import FreelancerListView,ExternalJobListView,ExternalJobDetailView,ApplyForJobView, ApplicationDecisionView


urlpatterns = [
    path('freelancers/', FreelancerListView.as_view(), name='freelancer-list'),
    path('viewjobs/', ExternalJobListView.as_view(), name='external-job-list'),
    path('viewajob/<int:job_id>/', ExternalJobDetailView.as_view(), name='external-job-detail'),
    path('apply/', ApplyForJobView.as_view(), name='apply-for-job'),
    path('applications/<int:application_id>/', ApplicationDecisionView.as_view(), name='application-decision'),

]

