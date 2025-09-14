from rest_framework import viewsets, permissions
from .models import Message
from .serializers import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # L’utilisateur voit seulement ses messages
        return Message.objects.filter(destinataire=self.request.user) | Message.objects.filter(expediteur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)
