from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.IntegerField()
    posted_by_user_id = models.IntegerField()
    milestones = models.IntegerField(help_text="Number of milestones for the job")
    job_level = models.CharField(max_length=100, help_text="Experience level required")
    work_hours = models.CharField(max_length=100, help_text="work hours required")
    education = models.CharField(max_length=100, help_text="Education level required")
    company_name = models.CharField(max_length=255, help_text="Name of the hiring company")

    def __str__(self):
        return self.title



class TaskSubmission(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    milestone = models.IntegerField()
    submission_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/%Y/%m/%d/', null=True, blank=True)
    link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Submission for job {self.job.title}, milestone {self.milestone}"

