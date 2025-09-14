from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    expediteur_email = serializers.ReadOnlyField(source="expediteur.email")
    destinataire_email = serializers.ReadOnlyField(source="destinataire.email")

    class Meta:
        model = Message
        fields = "__all__"
