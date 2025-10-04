from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, UserSerializer,
    ChangePasswordSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer
)
from .tokens import make_email_token, verify_email_token
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from Documents.models import Cni
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        token = make_email_token(user.id)
        verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"

        # Générer le contenu HTML avec le template
        html_content = render_to_string('emails/verify_email.html', {
            'verification_url': verify_url
        })

        # Envoyer l'email
        email = EmailMessage(
            subject="Vérification de votre email",
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = "html"  # Indique que le contenu est HTML
        email.send(fail_silently=False)
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        uid = verify_email_token(token)
        if not uid:
            return Response({"detail": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = True
        user.save()
        return Response({"detail": "Email vérifié. Vous pouvez maintenant vous connecter."})

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = self.get_object()

        # Supprimer l'ancienne CNI si elle existe
        if user.cni:
            user.cni.delete()

        # Récupérer les fichiers dans validated_data
        cni_recto = serializer.validated_data.pop("cni_recto", None)
        cni_verso = serializer.validated_data.pop("cni_verso", None)

        # Créer une nouvelle CNI si les deux fichiers sont présents
        if cni_recto and cni_verso:
            cni = Cni.objects.create(recto=cni_recto, verso=cni_verso)
            serializer.save(cni=cni)
        else:
            serializer.save()

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Mot de passe incorrect."]}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Mot de passe changé avec succès."})

# Password reset (request: send email with link)
class ResetPasswordRequestView(generics.GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Do not reveal existence
            return Response({"detail": "Si l'adresse existe, vous recevrez un email."})
        # create token using Django PasswordResetTokenGenerator and uid
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/?uid={uid}&token={token}"
        send_mail(
            subject="Réinitialisation de mot de passe",
            message=f"Réinitialisez: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({"detail": "Si l'adresse existe, vous recevrez un email."})

class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        uidb64 = ser.validated_data["uidb64"]
        token = ser.validated_data["token"]
        new_password = ser.validated_data["new_password"]

        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"detail": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Mot de passe réinitialisé avec succès."})
