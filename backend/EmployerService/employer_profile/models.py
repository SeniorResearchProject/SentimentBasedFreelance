from django.db import models

# Create your models here.
class Employer(models.Model):
    name = models.CharField(max_length=255)
    user_id = models.IntegerField() #foreign key
    comapanyName = models.CharField(max_length=255, null=True, blank=True)
    comapanyUrl= models.CharField(max_length=255,null=True, blank=True)
    logo = models.ImageField(upload_to='images/', null=True, blank=True)
    email = models.EmailField() #foreign key
    biography = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return self.name