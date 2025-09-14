from rest_framework import serializers
from .models import Transaction, Validation

class ValidationSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Validation
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    validations = ValidationSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
