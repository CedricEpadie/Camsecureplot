from django.db import models
from django.conf import settings
from parcelles.models import Parcelle

class Transaction(models.Model):
    ETATS = [
        ("draft", "Brouillon"),
        ("pending", "En attente validation"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
        ("completed", "Terminée"),
    ]
    etat = models.CharField(max_length=20, choices=ETATS, default="draft")
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(blank=True, null=True)

    acheteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="transactions_achetees",
        on_delete=models.CASCADE
    )
    vendeur = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="transactions_vendues",
        on_delete=models.CASCADE
    )
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name="transactions")

    def __str__(self):
        return f"Transaction {self.id} - {self.parcelle.titre}"
    
class Validation(models.Model):
    ROLES = [("notaire", "Notaire"), ("geometre", "Géomètre"), ("acheteur", "Acheteur"), ("vendeur", "Vendeur")]
    STATUTS = [("pending", "En attente"), ("approved", "Approuvé"), ("rejected", "Rejeté")]

    transaction = models.ForeignKey(Transaction, related_name="validations", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    statut = models.CharField(max_length=20, choices=STATUTS, default="pending")
    date_validation = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("transaction", "role")

    def __str__(self):
        return f"{self.role} - {self.transaction.id}"
