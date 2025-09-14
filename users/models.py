from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone
from .managers import CustomUserManager
from Documents.models import Cni

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("default_user", "Default_user"),
        ("notaire", "Notaire"),
        ("geometre", "Géomètre"),
        ("admin", "Administrateur"),
    ]

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=50, blank=True)
    prenom = models.CharField(max_length=50, blank=True)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # False until email verification
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="default_user")
    cni = models.OneToOneField(Cni, on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f"{self.prenom} {self.nom}".strip()

    def __str__(self):
        return self.email
