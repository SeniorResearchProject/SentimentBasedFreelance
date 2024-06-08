from django.urls import path
from .views import FreelancerRateView, SentimentAnalysisView,  EnglishSentimentAnalysisView, SentimentListView

urlpatterns = [
    path('analyze-sentiment/', SentimentAnalysisView, name='analyze_sentiment'),
    path('analyze-sentiment-english/', EnglishSentimentAnalysisView, name='analyze_sentiment'),
    path('sentiment/<int:freelancer_id>/', FreelancerRateView.as_view(), name='freelancer-sentiment'),
    path('sentiments/', SentimentListView.as_view(), name='all-sentiments'),
]



