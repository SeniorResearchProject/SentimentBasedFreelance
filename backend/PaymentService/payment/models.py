from django.db import models

class Transaction(models.Model):
    first_name = models.CharField(max_length=255)  
    last_name = models.CharField(max_length=255)
    freelancer = models.IntegerField(default=1, null=True, blank=True)
    employer = models.IntegerField(null=True, blank=True)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tx_ref = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('created', 'Created'), ('completed', 'Completed')], default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    

