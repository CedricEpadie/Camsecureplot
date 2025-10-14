from rest_framework import viewsets, permissions
from .models import Parcelle
from .serializers import ParcelleSerializer
from Documents.models import PlanLocalisation, PlanCadastral, TitreFoncier, CertificatHypotheque
from django.db.models import Q
class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        parcelle = serializer.save()
        proprietaires = self.request.data.getlist("proprietaires_id")      

        # Si admin, possibilité d’ajouter un propriétaire spécifique
        if self.request.user.role == "admin":
            proprietaires = self.request.data.get("proprietaires_id", [])
            if proprietaires:
                parcelle.proprietaires.add(*proprietaires)
        else:
            # Ajouter automatiquement le créateur comme propriétaire
            parcelle.proprietaires.add(self.request.user)
            parcelle.proprietaires.add(*proprietaires)

            
    def update(self, request, *args, **kwargs):
        partial = True
        return super().update(request, *args, **kwargs)
            
    def perform_update(self, serializer):
        parcelle = self.get_object()

        # Récupère les fichiers seulement si présents
        plan_cadastral = self.request.FILES.get("plan_cadastral", None)
        plan_localisation = self.request.FILES.get("plan_localisation", None)
        titre_foncier = self.request.FILES.get("titre_foncier", None)
        certificat_hypotheque = self.request.FILES.get("certificat_hypotheque", None)

        if plan_cadastral:
            if parcelle.plan_cadastral:
                parcelle.plan_cadastral.delete()
            plan_cadastral = PlanCadastral.objects.create(doc=plan_cadastral)
        else:
            plan_cadastral = parcelle.plan_cadastral

        if plan_localisation:
            if parcelle.plan_localisation:
                parcelle.plan_localisation.delete()
            plan_localisation = PlanLocalisation.objects.create(doc=plan_localisation)
        else:
            plan_localisation = parcelle.plan_localisation

        if titre_foncier:
            if parcelle.titre_foncier:
                parcelle.titre_foncier.delete()
            titre_foncier = TitreFoncier.objects.create(doc=titre_foncier)
        else:
            titre_foncier = parcelle.titre_foncier

        if certificat_hypotheque:
            if parcelle.certificat_hypotheque:
                parcelle.certificat_hypotheque.delete()
            certificat_hypotheque = CertificatHypotheque.objects.create(doc=certificat_hypotheque)
        else:
            certificat_hypotheque = parcelle.certificat_hypotheque

        # ⚡ Appel save avec partial=True pour éviter les validations strictes
        serializer.save(
            plan_cadastral=plan_cadastral,
            plan_localisation=plan_localisation,
            titre_foncier=titre_foncier,
            certificat_hypotheque=certificat_hypotheque,
        )


from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Parcelle
from .serializers import ParcelleSerializer

class UserParcelleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vue simple : retourne uniquement les parcelles
    liées à l'utilisateur connecté.
    """
    serializer_class = ParcelleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Parcelle.objects.filter(
            Q(proprietaires=user)
            | Q(charge_parcelle=user)
        ).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
