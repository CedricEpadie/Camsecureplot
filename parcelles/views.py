from rest_framework import viewsets, permissions
from .models import Parcelle
from .serializers import ParcelleSerializer
from Documents.models import PlanLocalisation, PlanCadastral, TitreFoncier, CertificatHypotheque

class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        parcelle = serializer.save()

        # Si admin, possibilité d’ajouter un propriétaire spécifique
        if self.request.user.role == "admin":
            proprietaires = self.request.data.get("proprietaires_id", [])
            if proprietaires:
                parcelle.proprietaires.add(*proprietaires)
        else:
            # Ajouter automatiquement le créateur comme propriétaire
            parcelle.proprietaires.add(self.request.user)
            
    def perform_update(self, serializer):
        parcelle = self.get_object()
        
        parcelle.plan_localisation.delete()
        parcelle.certificat_hypotheque.delete()
        parcelle.titre_foncier.delete()
        parcelle.plan_cadastral.delete()
        
        plan_cadastral = serializer.validated_data.pop("plan_cadastral", None)
        plan_localisation = serializer.validated_data.pop("plan_localisation", None)
        titre_foncier = serializer.validated_data.pop("titre_foncier", None)
        certificat_hypotheque = serializer.validated_data.pop("certificat_hypotheque", None)
        
        plan_cadastral = PlanCadastral.objects.create(doc=plan_cadastral)
        plan_localisation = PlanLocalisation.objects.create(doc=plan_localisation)
        titre_foncier = TitreFoncier.objects.create(doc=titre_foncier)
        certificat_hypotheque = CertificatHypotheque.objects.create(doc=certificat_hypotheque)
        
        serializer.save(plan_cadastral=plan_cadastral, plan_localisation=plan_localisation, titre_foncier=titre_foncier, certificat_hypotheque=certificat_hypotheque)
