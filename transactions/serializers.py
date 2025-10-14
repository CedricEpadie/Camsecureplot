from rest_framework import serializers
from .models import Transaction, Validation
from users.models import CustomUser
User=CustomUser

class ValidationSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Validation
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    acheteur = serializers.PrimaryKeyRelatedField(read_only=True)
    vendeurs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
