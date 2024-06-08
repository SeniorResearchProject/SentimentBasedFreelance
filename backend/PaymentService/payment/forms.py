from django import forms
from .models import Transaction

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['first_name', 'last_name', 'email', 'amount', 'tx_ref']
