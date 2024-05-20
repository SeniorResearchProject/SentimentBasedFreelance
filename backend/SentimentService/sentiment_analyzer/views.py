from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import CommentSerializer, SentimentSerializer
from .models import Analysis
import os
import re
import string
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from joblib import load
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view




# Load your model and its components
model_path = os.path.join(os.path.dirname(__file__), '../amharicnew_models.joblib')
model_components = load(model_path)
vectorizer = model_components['vectorizer']
tfidf = model_components['tfidf']
calibrated_sgd = model_components['calibrated_sgd']

@csrf_exempt  # Disable CSRF token for simplicity, consider security implications
def SentimentAnalysisView(request):
        #authentication_classes = [TokenAuthentication] 
        
    # Try to parse JSON data
   # Parse the JSON data
        data = JSONParser().parse(request)
        serializer = CommentSerializer(data=data)

        if serializer.is_valid():
            comment_text = serializer.validated_data['comment']
            freelancer_id = serializer.validated_data['freelancer_id']
        if not comment_text or not freelancer_id:
            return JsonResponse({'error': 'Missing comment or freelancer_id'}, status=400)
        
        # Transform and predict sentiment
        X_vec = vectorizer.transform([comment_text])
        X_tfidf = tfidf.transform(X_vec)
        prediction = calibrated_sgd.predict(X_tfidf)
        prediction_proba = calibrated_sgd.predict_proba(X_tfidf)

        # Assuming the 'Positive' class is the last one in your model
        positive_probability = prediction_proba[0][-1]
        if positive_probability < 0.5:
            class_label = 'Negative'
        else:
            class_label = 'Positive'

        sentiment_score = positive_probability

        # Create and save the comment object
        comment = Analysis(comment=comment_text, sentiment=class_label, freelancer_id=freelancer_id)
        comment.save()

        return JsonResponse({'message': 'Comment and sentiment saved successfully', 'sentiment': class_label, 'score': sentiment_score}, status=201)

@api_view(['GET'])
def freelancer_sentiment_view(request, freelancer_id):
    try:
        analyses = Analysis.objects.filter(freelancer_id=freelancer_id)
        if analyses.exists():
            # Using the SentimentSerializer to fetch only the sentiment field
            serializer = SentimentSerializer(analyses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No sentiment data found for this freelancer."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Load your model
# Load your model
model_path = os.path.join(os.path.dirname(__file__), '../stacking_sentiment_model.joblib')
pipeline, vectorizer = joblib.load(model_path)
# Preprocessing function
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Replace "n't" with "not" to handle cases like "isn't"
    text = re.sub(r"n't", " not", text)
    # Handle negations by appending "_not" to the following word
    text = re.sub(r"\b(not)\s+(\w+)\b", r"\1_\2", text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra whitespaces
    text = re.sub('\s+', ' ', text).strip()
    return text
@csrf_exempt 
def EnglishSentimentAnalysisView(request):
    # Parse the JSON data
    data = JSONParser().parse(request)
    serializer = CommentSerializer(data=data)

    if serializer.is_valid():
        comment_text = serializer.validated_data['comment']
        freelancer_id = serializer.validated_data['freelancer_id']
        if not comment_text or not freelancer_id:
            return JsonResponse({'error': 'Missing comment or freelancer_id'}, status=400)
        
        # Preprocess and predict sentiment
        comment_preprocessed = preprocess_text(comment_text)
        text_vectorized = vectorizer.transform([comment_preprocessed])
        prediction_proba = pipeline.predict_proba(text_vectorized)

        # Assuming the 'Positive' class is the last one in your model
        positive_probability = prediction_proba[0][-1]
        if positive_probability < 0.5:
            class_label = 'Negative'
        else:
            class_label = 'Positive'

        sentiment_score = positive_probability
        rate = int(sentiment_score * 10) + 1

        # Create and save the comment object
        comment = Analysis(comment=comment_text, sentiment=class_label, freelancer_id=freelancer_id,  rate=rate)
        comment.save()

        return JsonResponse({'message': 'Comment and sentiment saved successfully', 'sentiment': class_label, 'score': sentiment_score,'rate': rate}, status=201)

    return JsonResponse({'error': 'Invalid data'}, status=400)
