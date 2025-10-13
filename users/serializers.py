from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from Documents.models import Cni

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    cni_recto = serializers.FileField(write_only=True, required=True)
    cni_verso = serializers.FileField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ("id", "email", "nom", "prenom", "telephone", "role", "is_active", "date_joined", "cni_recto", "cni_verso")
        read_only_fields = ("is_active", "date_joined", "id")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[password_validation.validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    cni_recto = serializers.FileField(write_only=True, required=True)
    cni_verso = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "nom", "prenom", "telephone", "role", "password", "password2", "cni_recto", "cni_verso")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        cni_recto = validated_data.pop('cni_recto')
        cni_verso = validated_data.pop('cni_verso')
        
        user = User.objects.create_user(password=password, **validated_data)
        user.is_active = False  # require email validation
        
        cni = Cni.objects.create(recto=cni_recto, verso=cni_verso)
        user.cni = cni
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[password_validation.validate_password])

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[password_validation.validate_password])
class UserSerializer2(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "nom", "prenom", "full_name", "role"]

    def get_full_name(self, obj):
        return f"{obj.prenom} {obj.nom}".strip()
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nom', 'prenom', 'telephone', 'role']