from django.db import models
from django.conf import settings
from parcelles.models import Parcelle  # adapte selon ton arborescence

class Transaction(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)

    # Acheteur unique
    acheteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="transactions_achetees",
        on_delete=models.CASCADE
    )

    # Plusieurs vendeurs
    vendeurs = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="transactions_vendues"
    )

    notaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="transactions_notaire",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    geometre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="transactions_geometre",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    etat = models.CharField(max_length=20, default="draft")
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)

class Validation(models.Model):
    ROLES = [("notaire", "Notaire"), ("geometre", "Géomètre"), ("acheteur", "Acheteur"), ("vendeur", "Vendeur")]
    STATUTS = [("pending", "En attente"), ("approved", "Approuvé"), ("rejected", "Rejeté")]

    transaction = models.ForeignKey(Transaction, related_name="validations", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    statut = models.CharField(max_length=20, choices=STATUTS, default="pending")
    date_validation = models.DateTimeField(auto_now=True)

    class Meta:
       unique_together = ("transaction", "role", "user")

    def __str__(self):
        return f"{self.role} - {self.transaction.id}"
