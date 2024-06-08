from django.db import models
from datetime import datetime, timedelta

class Job(models.Model):
    TITLE_CHOICES = [
        ('partTime', 'Part-Time'),
        ('fullTime', 'Full-Time'),
    ]

    JOB_LEVEL_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    EDUCATION_LEVEL_CHOICES = [
        ('primary-education', 'Primary Education'),
        ('higher-education', 'Higher Education'),
        ('graduate-degree', 'Graduate Degree'),
        ('masters-degree', 'Masters Degree'),
        ('doctoral-degree', 'Doctoral Degree'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    job_type = models.CharField(max_length=50, choices=TITLE_CHOICES,null=True, blank=True)
    min_budget = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    max_budget = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    posted_by_user_id = models.IntegerField()  # ForeignKey can be used for real relationships
    education = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, help_text="Education level required",null=True, blank=True)
    milestones = models.PositiveIntegerField(help_text="Number of milestones for the job",null=True, blank=True)
    job_level = models.CharField(max_length=50, choices=JOB_LEVEL_CHOICES, help_text="Job difficulty level (hard, medium, or easy)",null=True, blank=True)
    
    
    comapanyName = models.CharField(max_length=255,null=True, blank=True)
    location = models.CharField(max_length=255,null=True, blank=True)
    posted_at= models.DateTimeField(auto_now=True)
    


    def __str__(self):
        return self.title






# class TaskSubmission(models.Model):
#     freelancer_name = models.CharField(max_length=255)
#     freelancer= models.IntegerField() #the id of the freelancer who submit the task
#     job_id = models.IntegerField() #the id of the job that the freelancer make submission to
#     milestone = models.PositiveIntegerField() # get the milestone from the tasksubmission milestone field of the specific job
#     submited_date = models.DateTimeField() # get it when a user submit the task from freelancerservice
#     file = models.FileField(upload_to='submissions/%Y/%m/%d/') # get it when a user submit the task from freelancerservice
#     link = models.CharField(max_length=255) # get it when a user submit the task from freelancerservice
#     job_applied= models.IntegerField() # get it  when a user submit the task from freelancerservice exactly from the frontend as param
#     job_title = models.CharField(max_length=255) # get the title from the tasksubmission job_title field of the specific job
#     comment = models.CharField(max_length=255) #the comment the emplyer give for that specific task submission
    

#     def __str__(self):
#         return f"Submission for job {self.job_id }, milestone {self.milestone}"

