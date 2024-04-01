from django.db import models
class Review(models.Model):
         user = models.ForeignKey('user_management.User', related_name='reviews', on_delete=models.CASCADE)
         text = models.TextField()
         rating = models.IntegerField()  # You can adjust the field based on your rating system
         created_at = models.DateTimeField(auto_now_add=True)
         # Add other fields as needed for sentiment analysis
