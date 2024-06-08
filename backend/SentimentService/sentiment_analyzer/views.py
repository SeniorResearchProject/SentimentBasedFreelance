from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import CommentSerializer, SentimentSerializer, FreelancerSerializer, AllSentimentSerializer
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
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import requests
from django.conf import settings




# Load your model and its components
# model_path = os.path.join(os.path.dirname(__file__), '../amharicnew_models.joblib')
# model_components = load(model_path)
# vectorizer = model_components['vectorizer']
# tfidf = model_components['tfidf']
# calibrated_sgd = model_components['calibrated_sgd']

model_path_amharic= os.path.join(os.path.dirname(__file__), '../amharicnew_models.joblib')
model_components = load(model_path_amharic)
vectorizer_amharic = model_components['vectorizer']
tfidf_amharic = model_components['tfidf']
calibrated_sgd_amharic = model_components['calibrated_sgd']

# @csrf_exempt  # Disable CSRF token for simplicity, consider security implications
# def SentimentAnalysisView(request):
#         #authentication_classes = [TokenAuthentication] 
        
#     # Try to parse JSON data
#    # Parse the JSON data
#         data = JSONParser().parse(request)
#         serializer = CommentSerializer(data=data)

#         if serializer.is_valid():
#             comment_text = serializer.validated_data['comment']
#             freelancer_id = serializer.validated_data['freelancer_id']
#         if not comment_text or not freelancer_id:
#             return JsonResponse({'error': 'Missing comment or freelancer_id'}, status=400)
        
#         # Transform and predict sentiment
#         X_vec = vectorizer_amharic.transform([comment_text])
#         X_tfidf = tfidf_amharic.transform(X_vec)
#         prediction = calibrated_sgd_amharic.predict(X_tfidf)
#         prediction_proba = calibrated_sgd_amharic.predict_proba(X_tfidf)

#         # Assuming the 'Positive' class is the last one in your model
#         positive_probability = prediction_proba[0][-1]
#         if positive_probability < 0.5:
#             class_label = 'Negative'
#         else:
#             class_label = 'Positive'

#         sentiment_score = positive_probability

#         # Create and save the comment object
#         comment = Analysis(comment=comment_text, sentiment=class_label, freelancer_id=freelancer_id)
#         comment.save()

#         return JsonResponse({'message': 'Comment and sentiment saved successfully', 'sentiment': class_label, 'score': sentiment_score}, status=201)
# @api_view(['GET'])
# def freelancer_sentiment_view(request, freelancer_id):
#     try:
#         analyses = Analysis.objects.filter(freelancer_id=freelancer_id)
#         if analyses.exists():
#             # Using the SentimentSerializer to fetch only the sentiment field
#             serializer = SentimentSerializer(analyses, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response({"message": "No sentiment data found for this freelancer."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # Load your model
# # Load your model
# model_path = os.path.join(os.path.dirname(__file__), '../stacking_sentiment_model.joblib')
# pipeline, vectorizer = joblib.load(model_path)
# # Preprocessing function
# def preprocess_text(text):
#     # Convert to lowercase
#     text = text.lower()
#     # Replace "n't" with "not" to handle cases like "isn't"
#     text = re.sub(r"n't", " not", text)
#     # Handle negations by appending "_not" to the following word
#     text = re.sub(r"\b(not)\s+(\w+)\b", r"\1_\2", text)
#     # Remove punctuation
#     text = text.translate(str.maketrans('', '', string.punctuation))
#     # Remove extra whitespaces
#     text = re.sub('\s+', ' ', text).strip()
#     return text
# @csrf_exempt 
# def EnglishSentimentAnalysisView(request):
#     # Parse the JSON data
#     data = JSONParser().parse(request)
#     serializer = CommentSerializer(data=data)

#     if serializer.is_valid():
#         comment_text = serializer.validated_data['comment']
#         freelancer_id = serializer.validated_data['freelancer_id']
#         if not comment_text or not freelancer_id:
#             return JsonResponse({'error': 'Missing comment or freelancer_id'}, status=400)
        
#         # Preprocess and predict sentiment
#         comment_preprocessed = preprocess_text(comment_text)
#         text_vectorized = vectorizer.transform([comment_preprocessed])
#         prediction_proba = pipeline.predict_proba(text_vectorized)

#         # Assuming the 'Positive' class is the last one in your model
#         positive_probability = prediction_proba[0][-1]
#         if positive_probability < 0.5:
#             class_label = 'Negative'
#         else:
#             class_label = 'Positive'

#         sentiment_score = positive_probability
#         rate = int(sentiment_score * 10) + 1

#         # Create and save the comment object
#         comment = Analysis(comment=comment_text, sentiment=class_label, freelancer_id=freelancer_id,  rate=rate)
#         comment.save()

#         return JsonResponse({'message': 'Comment and sentiment saved successfully', 'sentiment': class_label, 'score': sentiment_score,'rate': rate}, status=201)

#     return JsonResponse({'error': 'Invalid data'}, status=400)




@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def SentimentAnalysisView(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        # Extract individual fields
        comment_text = data.get('comment')
        task_idd = data.get('task')
        # freelancer_id = data.get('freelancer_id')
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers

        if not comment_text:
            return JsonResponse({'error': 'Comment is required.'}, status=400)
        if not task_idd:
            return JsonResponse({'error': 'Task ID is required.'}, status=400)
        # if not freelancer_id:
        #     return JsonResponse({'error': 'Freelancer ID is required.'}, status=400)

        try:
            task_id = int(task_idd)
        except ValueError:
            return JsonResponse({'error': 'Invalid Task ID format.'}, status=400)

        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if not user_info.get('user_id'):
            return JsonResponse({'error': 'Invalid token. User authentication failed.'}, status=401)

        employer = user_info['user_id']

        # Validate the task by making a request to FreelancerMicroservice
        submission_response = requests.get(f'http://localhost:8002/api/get-submission/{task_id}/')

        if submission_response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch submission details.'}, status=submission_response.status_code)

        submission_data = submission_response.json()

        # Ensure the task matches
        if submission_data['id'] != task_id:
            return JsonResponse({'error': 'Task ID mismatch.'}, status=400)

        # if submission_data['freelancer'] != freelancer_id:
        #     return JsonResponse({'error': 'Freelancer ID mismatch.'}, status=400)
        
        freelancer_id =submission_data['freelancer']

        # Prepare data for serializer
        serializer_data = {
            'task': task_id,
            'comment': comment_text,
            'freelancer_id': freelancer_id
        }

        # Validate with serializer
        serializer = FreelancerSerializer(data=serializer_data)
        if serializer.is_valid():
            # Transform and predict sentiment
            X_vec = vectorizer_amharic.transform([comment_text])
            X_tfidf = tfidf_amharic.transform(X_vec)
            prediction = calibrated_sgd_amharic.predict(X_tfidf)
            prediction_proba = calibrated_sgd_amharic.predict_proba(X_tfidf)

            # Assuming the 'Positive' class is the last one in your model
            positive_probability = prediction_proba[0][-1]
            class_label = 'Positive' if positive_probability >= 0.5 else 'Negative'
            sentiment_score = positive_probability
            rate = int(sentiment_score * 10) + 1

            # Create and save the comment object
            comment = Analysis(
                employer=employer,
                task=task_id,
                comment=comment_text,
                sentiment=class_label,
                freelancer_id=freelancer_id,
                sentiment_score=sentiment_score,
                rate=rate
            )
            comment.save()

            return JsonResponse({'message': 'Comment and sentiment saved successfully', 'sentiment': class_label, 'score': sentiment_score, 'rate': rate}, status=201)
        else:
            return JsonResponse({'error': 'Invalid data', 'details': serializer.errors}, status=400)

# View to retrieve sentiment analysis for a freelancer
# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def freelancer_sentiment_view(request, freelancer_id):
#     try:
#         analyses = Analysis.objects.filter(freelancer_id=freelancer_id)
#         if analyses.exists():
#             serializer = SentimentSerializer(analyses, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response({"message": "No sentiment data found for this freelancer."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def EnglishSentimentAnalysisView(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        # logger.debug(f"Received data: {data}")

        # Extract individual fields
        comment_text = data.get('comment')
        task_idd = data.get('task')
        # freelancer_id = data.get('freelancer_id')
        token = request.META.get('HTTP_AUTHORIZATION')  # Extract the token from the request headers

        if not comment_text:
            return Response({'error': 'Comment is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not task_idd:
            return Response({'error': 'Task ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # if not freelancer_id:
        #     return Response({'error': 'Freelancer ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task_id = int(task_idd)
        except ValueError:
            return Response({'error': 'Invalid Task ID format.'}, status=status.HTTP_400_BAD_REQUEST)

        user_info = requests.get(f'{settings.USER_MANAGEMENT_URL}/api/token/validate/', headers={'Authorization': token}).json()

        if not user_info.get('user_id'):
            return Response({'error': 'Invalid token. User authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

        employer = user_info['user_id']

        # Validate the task by making a request to FreelancerMicroservice
        submission_response = requests.get(f'http://localhost:8002/api/get-submission/{task_id}/')

        if submission_response.status_code != 200:
            return Response({'error': 'Failed to fetch submission details.'}, status=submission_response.status_code)

        submission_data = submission_response.json()

        # Ensure the task matches
        if submission_data['id'] != task_id:
            return Response({'error': 'Task ID mismatch.'}, status=status.HTTP_400_BAD_REQUEST)

        # if submission_data['freelancer'] != freelancer_id:
        #     return Response({'error': 'Freelancer ID mismatch.'}, status=status.HTTP_400_BAD_REQUEST)
        
        freelancer_id =submission_data['freelancer']

        # Prepare data for serializer
        serializer_data = {
            'task': task_id,
            'comment': comment_text,
            'freelancer_id': freelancer_id
        }

        # Validate with serializer
        serializer = FreelancerSerializer(data=serializer_data)
        if serializer.is_valid():
            # Preprocess and predict sentiment
            comment_preprocessed = preprocess_text(comment_text)
            text_vectorized = vectorizer.transform([comment_preprocessed])
            prediction_proba = pipeline.predict_proba(text_vectorized)

            # Assuming the 'Positive' class is the last one in your model
            positive_probability = prediction_proba[0][-1]
            class_label = 'Positive' if positive_probability >= 0.5 else 'Negative'

            sentiment_score = positive_probability
            rate = int(sentiment_score * 10) + 1

            # Create and save the comment object
            comment = Analysis(
                employer=employer,
                task=task_id,
                comment=comment_text,
                sentiment=class_label,
                freelancer_id=freelancer_id,
                sentiment_score=sentiment_score,
                rate=rate
            )
            comment.save()

            return Response({'message': 'Comment and sentiment saved successfully', 'sentiment': class_label, 'score': sentiment_score, 'rate': rate}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FreelancerRateView(APIView):

    def get(self, request, freelancer_id):
        # Retrieve all Analysis objects for the specific freelancer
        analysis_objects = Analysis.objects.filter(freelancer_id=freelancer_id)
        
        if not analysis_objects.exists():
            return JsonResponse({'error': 'No ratings found for the specified freelancer.'}, status=404)

        # Calculate the average rate
        total_rate = sum(analysis.rate for analysis in analysis_objects)
        count = analysis_objects.count()
        average_rate = total_rate / count if count > 0 else 0

        # Update the sentiment_score for each Analysis object
        analysis_objects.update(sentiment_score=average_rate)

        return JsonResponse({
            'freelancer_id': freelancer_id,
            'average_rate': average_rate,
            'message': 'Sentiment scores updated successfully'
        }, status=200)
    

class SentimentListView(APIView):
    def get(self, request):
        sentiments = Analysis.objects.all()
        serializer = AllSentimentSerializer(sentiments, many=True)
        return Response(serializer.data)