from rest_framework import serializers
from .models import Analysis

class CommentSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True)
    freelancer_id = serializers.CharField(required=True)
    sentiment = serializers.ChoiceField(choices=['positive', 'negative'], required=False, allow_blank=True)


class SentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ['sentiment']
