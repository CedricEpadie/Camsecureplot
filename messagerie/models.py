from django.db import models
from django.conf import settings
from parcelles.models import Parcelle

class Message(models.Model):
    expediteur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages_envoyes", on_delete=models.CASCADE)
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages_recus", on_delete=models.CASCADE)
    parcelle = models.ForeignKey(Parcelle, related_name="messages", on_delete=models.CASCADE, null=True, blank=True)
    contenu = models.TextField()
    date_envoie = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Msg de {self.expediteur} à {self.destinataire}"
