from django.db import models


class Freelancer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    TYPE_CHOICES = [
        ('FULL-TIME', 'FULL-TIME'),
        ('PART-TIME', 'PART-TIME'),
    ]
    name = models.CharField(max_length=255)
    experience = models.IntegerField(help_text="Experience in years",null=True, blank=True)
    user_id = models.IntegerField() #foreign key
    profession = models.CharField(max_length=255, null=True, blank=True)
    education_level = models.CharField(max_length=255, null=True, blank=True)
    available = models.BooleanField(default=True, help_text="Availability for new projects")
    website = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    cv = models.FileField(upload_to='files/', null=True, blank=True)
    Nationality = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    email = models.EmailField() #foreign key
    date_of_birth = models.DateField(null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    salary_range = models.CharField(max_length=255, null=True, blank=True)
    employeeType = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True, blank=True)
    skill = models.TextField(null=True, blank=True)
    rate = models.FloatField(default=0.0)


    def __str__(self):
        return self.name



class JobApplication(models.Model):
    freelancer = models.IntegerField()
    freelancer_name = models.CharField(max_length=255)
    job_id = models.IntegerField()  # Assuming job IDs are integers and you'll use them to interface with the employer service
    job_title = models.CharField(max_length=255)
    dateApplied = models.DateTimeField(auto_now=True)
    milestone = models.PositiveIntegerField(default=2)
    cv = models.FileField(upload_to='files/', null=True, blank=True)
    cover_letter = models.TextField()
    application_status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ), default='pending')

    def __str__(self):
        return f"{self.freelancer.id}'s application for Job ID {self.job_id}"


class TaskSubmission(models.Model):
    freelancer = models.IntegerField()
    freelancer_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_applied= models.IntegerField()
    job_id = models.IntegerField()
    milestone = models.PositiveIntegerField()
    submission_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/%Y/%m/%d/', null=True, blank=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Submission for job {self.job_id}, milestone {self.milestone}"



