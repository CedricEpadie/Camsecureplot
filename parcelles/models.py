from django.db import models
from django.conf import settings
from Documents.models import PlanLocalisation, PlanCadastral, TitreFoncier, CertificatHypotheque

class Parcelle(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    taille_m2 = models.FloatField()
    prix_m2 = models.DecimalField(max_digits=12, decimal_places=2)
    localisation = models.TextField()
    statut = models.CharField(max_length=50, choices=[
        ("available", "Disponible"),
        ("sold", "Vendu"),
        ("pending", "En cours")
    ], default="available")
    adresse = models.CharField(max_length=255, blank=True, null=True)
    type_droit_propriete = models.CharField(max_length=100, blank=True, null=True)
    usage = models.CharField(max_length=100, blank=True, null=True)
    date_eng = models.DateField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    charge_parcelle = models.TextField(blank=True, null=True)
    coordonnees = models.TextField(help_text="Liste de coordonnées GeoJSON")
    
    # Document liées à la parcelle
    plan_localisation = models.ForeignKey(PlanLocalisation, on_delete=models.SET_NULL, blank=True, null=True)
    titre_foncier = models.ForeignKey(TitreFoncier, on_delete=models.SET_NULL, blank=True, null=True)
    plan_cadastral = models.ForeignKey(PlanCadastral, on_delete=models.SET_NULL, blank=True, null=True)
    certificat_hypotheque = models.ForeignKey(CertificatHypotheque, on_delete=models.SET_NULL, blank=True, null=True)

    # Relations
    proprietaires = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Possession",
        related_name="parcelles"
    )

    def __str__(self):
        return f"{self.titre} ({self.taille_m2} m²)"

class Possession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    date_acquisition = models.DateTimeField(auto_now_add=True)