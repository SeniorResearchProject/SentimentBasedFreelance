from django.urls import path
from .views import freelancer_sentiment_view, SentimentAnalysisView,  EnglishSentimentAnalysisView

urlpatterns = [
    path('analyze-sentiment/', SentimentAnalysisView, name='analyze_sentiment'),
    path('analyze-sentiment-english/', EnglishSentimentAnalysisView, name='analyze_sentiment'),
    path('sentiment/<int:freelancer_id>/', freelancer_sentiment_view, name='freelancer-sentiment'),
]



