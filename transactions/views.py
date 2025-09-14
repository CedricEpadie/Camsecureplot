from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Transaction, Validation
from .serializers import TransactionSerializer, ValidationSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def valider(self, request, pk=None):
        """
        Permet à un notaire ou géomètre de valider/rejeter une transaction
        """
        transaction = self.get_object()
        
        if transaction.acheteur == request.user:
            role = "acheteur"
        elif transaction.vendeur == request.user:
            role = "vendeur"
        else:
            role = request.user.role
            
        statut = request.data.get("statut")

        validation, created = Validation.objects.get_or_create(
            transaction=transaction, role=role, user=request.user
        )
        validation.statut = statut
        validation.save()

        # Si tous les concernés ont validé, on passe la transaction à l'état "approved"
        if transaction.validations.filter(statut="approved").count() == 4:
            transaction.etat = "approved"
            transaction.save()

        return Response(ValidationSerializer(validation).data)
