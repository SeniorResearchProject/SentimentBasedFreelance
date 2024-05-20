from django.db import models


class Freelancer(models.Model):
    freelancer_id = models.AutoField(primary_key=True)
    freelancer_name = models.CharField(max_length=255)
    experience = models.IntegerField(help_text="Experience in years")
    # You can add more fields as needed, such as:
    skills = models.TextField(help_text="List of skills")
    available = models.BooleanField(default=True, help_text="Availability for new projects")

    def __str__(self):
        return self.freelancer_name



class JobApplication(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='applications')
    job_id = models.IntegerField()  # Assuming job IDs are integers and you'll use them to interface with the employer service
    cover_letter = models.TextField()
    application_status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ), default='pending')

    def __str__(self):
        return f"{self.freelancer.freelancer_name}'s application for Job ID {self.job_id}"
