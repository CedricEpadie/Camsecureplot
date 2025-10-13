import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # Récupérer l'user_id depuis l'URL
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        # Chaque utilisateur a son propre groupe
        self.user_group_name = f"user_{self.user_id}"

        # Rejoindre le groupe personnel de l'utilisateur
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

        print(f"✅ User {self.user_id} connecté au WebSocket")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        print(f"❌ User {self.user_id} déconnecté du WebSocket")

    async def receive(self, text_data):
        data = json.loads(text_data)
        contenu = data.get("contenu")
        expediteur_id = data.get("expediteur")
        destinataire_id = data.get("destinataire")
        parcelle_id = data.get("parcelle")

        if not contenu:
            print("⚠️ Aucun contenu reçu :", data)
            return

        print(f"📨 Message reçu de {expediteur_id} vers {destinataire_id}: {contenu}")

        # Sauvegarde du message
        message = await self.save_message(expediteur_id, destinataire_id, contenu, parcelle_id)

        print(f"💾 Message sauvegardé avec ID: {message['id']}")

        # ✅ IMPORTANT : Envoyer au groupe de l'EXPÉDITEUR
        await self.channel_layer.group_send(
            f"user_{expediteur_id}",
            {
                "type": "chat_message",
                **message,
            },
        )
        print(f"📤 Message envoyé au groupe user_{expediteur_id}")

        # ✅ IMPORTANT : Envoyer au groupe du DESTINATAIRE
        await self.channel_layer.group_send(
            f"user_{destinataire_id}",
            {
                "type": "chat_message",
                **message,
            },
        )
        print(f"📤 Message envoyé au groupe user_{destinataire_id}")

    async def chat_message(self, event):
        # Retirer 'type' avant d'envoyer au client
        message_data = {k: v for k, v in event.items() if k != 'type'}
        await self.send(text_data=json.dumps(message_data))
        print(f"📬 Message transmis au client: {message_data}")

    @sync_to_async
    def save_message(self, expediteur_id, destinataire_id, contenu, parcelle_id=None):
        from django.contrib.auth import get_user_model
        from .models import Message
        from parcelles.models import Parcelle

        User = get_user_model()
        expediteur = User.objects.get(id=expediteur_id)
        destinataire = User.objects.get(id=destinataire_id)
        parcelle = Parcelle.objects.get(id=parcelle_id) if parcelle_id else None

        message = Message.objects.create(
            expediteur=expediteur,
            destinataire=destinataire,
            contenu=contenu,
            parcelle=parcelle,
        )
        
        # ⚠️ IMPORTANT : Inclure les emails pour le frontend
        return {
            "id": message.id,
            "contenu": message.contenu,
            "expediteur": expediteur.id,
            "destinataire": destinataire.id,
            "expediteur_email": expediteur.email,
            "destinataire_email": destinataire.email,
            "parcelle": parcelle.id if parcelle else None,
            "date_envoie": message.date_envoie.isoformat(),
            "est_lu": message.est_lu,
        }