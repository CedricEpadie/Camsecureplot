from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Transaction, Validation
from .serializers import TransactionSerializer, ValidationSerializer
import io, zipfile
from parcelles.models import Parcelle
from django.http import HttpResponse
from rest_framework import status
import random
from users.models import CustomUser
from django.db.models import Q
User=CustomUser

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        parcelle_id = request.data.get("parcelle")
        parcelle = Parcelle.objects.get(id=parcelle_id)
        
        acheteur_id =  request.data.get("acheteur")
        acheteur = User.objects.get(id=acheteur_id)

        # Créer la transaction
        transaction = Transaction.objects.create(
            parcelle=parcelle,
            acheteur=acheteur,
        )

        # Ajouter tous les propriétaires comme vendeurs
        vendeurs = parcelle.proprietaires.all()
        transaction.vendeurs.set(vendeurs)

        # Exclure l'acheteur et les vendeurs pour le notaire et le géomètre
        exclusion_ids = list(vendeurs.values_list('id', flat=True)) + [request.user.id]

        # Sélection aléatoire d'un notaire
        notaires = User.objects.filter(role="notaire", is_active=True).exclude(id__in=exclusion_ids)
        transaction.notaire = random.choice(notaires) if notaires.exists() else None

        # Sélection aléatoire d'un géomètre
        geometres = User.objects.filter(role="geometre", is_active=True).exclude(id__in=exclusion_ids)
        transaction.geometre = random.choice(geometres) if geometres.exists() else None

        transaction.save()
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def participants_validation(self, request, pk=None):
        """
        Retourne les détails de la transaction + les participants avec leurs statuts de validation.
        """
        transaction = self.get_object()

        # --- Helper pour récupérer l’état d’un participant ---
        def get_validation_status(user, role_name):
            v = Validation.objects.filter(transaction=transaction, user=user, role=role_name).first()
            return {
                "id": user.id,
                "email": user.email,
                "nom": user.get_full_name(),
                "role": role_name,
                "statut": v.statut if v else "pending",
                "date_validation": v.date_validation if v else None
            }

        participants = []

        # Acheteur
        participants.append(get_validation_status(transaction.acheteur, "acheteur"))

        # Vendeurs
        for vendeur in transaction.vendeurs.all():
            participants.append(get_validation_status(vendeur, "vendeur"))

        # Notaire
        if getattr(transaction, "notaire", None):
            participants.append(get_validation_status(transaction.notaire, "notaire"))

        # Géomètre
        if getattr(transaction, "geometre", None):
            participants.append(get_validation_status(transaction.geometre, "geometre"))

        # Calcul du pourcentage de validation
        total = len(participants)
        valides = sum(1 for p in participants if p["statut"] == "approved")
        progression = round((valides / total) * 100, 2) if total > 0 else 0

        # Sérialiser les infos principales de la transaction
        transaction_data = TransactionSerializer(transaction).data

        return Response({
            "transaction": transaction_data,
            "participants": participants,
            "progression": progression
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def valider(self, request, pk=None):
        transaction = self.get_object()
        user = request.user

        # 🔹 Déterminer le rôle du user pour cette transaction
        if user == transaction.acheteur:
            role = "acheteur"
        elif user in transaction.vendeurs.all():
            role = "vendeur"
        elif user.role in ["notaire", "geometre"]:
            role = user.role
        else:
            return Response({"error": "User not authorized for this transaction"}, status=status.HTTP_403_FORBIDDEN)

        # 🔹 Vérifier le statut envoyé
        statut = request.data.get("statut")
        if statut not in ["approved", "rejected"]:
            return Response({"error": "Invalid statut"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Créer ou mettre à jour la validation
        validation, created = Validation.objects.get_or_create(
            transaction=transaction,
            role=role,
            user=user,
            defaults={"statut": statut}
        )
        if not created:
            validation.statut = statut
            validation.save()

        # 🔹 Vérifier si tous les participants ont validé
        participants = list(transaction.vendeurs.all()) + [transaction.acheteur]
        if transaction.notaire:
            participants.append(transaction.notaire)
        if transaction.geometre:
            participants.append(transaction.geometre)

        all_validated = True
        for participant in participants:
            # On vérifie si chaque participant a validé
            v = Validation.objects.filter(transaction=transaction, user=participant, statut="approved").first()
            if not v:
                all_validated = False
                break

        # 🔹 Si tout le monde a validé -> approuver la transaction
        if all_validated:
            transaction.etat = "approved"
            transaction.save()

        return Response(ValidationSerializer(validation).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="documents/download", permission_classes=[permissions.IsAuthenticated])
    def download_documents(self, request, pk=None):
        transaction = self.get_object()
        parcelle = transaction.parcelle

        buffer = io.BytesIO()

        def add_file(zipf, file_field, name):
            """Ajoute un fichier dans le ZIP si existant"""
            if file_field and hasattr(file_field, "open"):
                file_field.open("rb")
                zipf.writestr(name, file_field.read())
                file_field.close()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            # =======================================================
            # 📁 Sous-dossier : Documents de la parcelle
            # =======================================================
            parcelle_dir = "Parcelle/"
            if parcelle.titre_foncier:
                add_file(zipf, parcelle.titre_foncier.doc, parcelle_dir + "titre_foncier.pdf")
            if parcelle.plan_cadastral:
                add_file(zipf, parcelle.plan_cadastral.doc, parcelle_dir + "plan_cadastral.pdf")
            if parcelle.plan_localisation:
                add_file(zipf, parcelle.plan_localisation.doc, parcelle_dir + "plan_localisation.pdf")
            if parcelle.certificat_hypotheque:
                add_file(zipf, parcelle.certificat_hypotheque.doc, parcelle_dir + "certificat_hypotheque.pdf")

            # =======================================================
            # 👥 Sous-dossier : Participants
            # =======================================================
            participants_dir = "Participants/"

            def add_cni(user, role_name):
                """Ajoute les fichiers CNI d'un utilisateur dans son sous-dossier"""
                if user and hasattr(user, "cni") and user.cni:
                    cni = user.cni
                    user_dir = f"{participants_dir}{role_name}/"
                    if cni.recto:
                        add_file(zipf, cni.recto, user_dir + "CNI_recto.jpg")
                    if cni.verso:
                        add_file(zipf, cni.verso, user_dir + "CNI_verso.jpg")

            # ✅ Acheteur (maintenant unique)
            add_cni(transaction.acheteur, "Acheteur")

            # ✅ Tous les vendeurs
            for v in transaction.vendeurs.all():
                add_cni(v, f"Vendeur_{v.id}")  # Optionnel : tu peux mettre le nom ou email pour distinguer

            # ✅ Notaire et géomètre
            if getattr(transaction, "notaire", None):
                add_cni(transaction.notaire, "Notaire")
            if getattr(transaction, "geometre", None):
                add_cni(transaction.geometre, "Geometre")

            # =======================================================
            # 🧾 Sous-dossier : Autres validateurs
            # =======================================================
            autres_dir = "Autres_Validateurs/"
            validations = Validation.objects.filter(transaction=transaction).select_related("user")
            known_users = {
                transaction.acheteur,
                *transaction.vendeurs.all(),
                getattr(transaction, "notaire", None),
                getattr(transaction, "geometre", None),
            }

            for v in validations:
                user = v.user
                if user not in known_users and hasattr(user, "cni") and user.cni:
                    cni = user.cni
                    email = user.email.replace("@", "_at_")
                    if cni.recto:
                        add_file(zipf, cni.recto, autres_dir + f"{email}_CNI_recto.jpg")
                    if cni.verso:
                        add_file(zipf, cni.verso, autres_dir + f"{email}_CNI_verso.jpg")

        # =======================================================
        # 📦 Réponse finale ZIP
        # =======================================================
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="transaction_{transaction.id}_documents.zip"'
        return response
    
class UserTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vue simple : retourne uniquement les transactions
    liées à l'utilisateur connecté.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            Q(acheteur=user)
            | Q(vendeurs=user)
            | Q(notaire=user)
            | Q(geometre=user)
        ).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)