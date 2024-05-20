from django.db import models

class Analysis(models.Model):
    comment = models.TextField()
    sentiment = models.CharField(max_length=255, blank=True, null=True)
    freelancer_id = models.IntegerField()  # Assuming freelancer IDs are integers
    sentiment_score = models.FloatField(default=0.0)  # Sentiment score field
    rate = models.IntegerField(default=0)  # Rate field

    def __str__(self):
        return f"Analysis for Freelancer ID {self.freelancer_id}"

