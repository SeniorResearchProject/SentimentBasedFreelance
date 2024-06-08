from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'first_name', 'last_name' ,'email', 'amount', 'tx_ref', 'status', 'created_at')
