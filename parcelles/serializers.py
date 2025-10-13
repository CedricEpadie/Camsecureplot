from rest_framework import serializers
from .models import Parcelle
from transactions.models import Transaction, Validation
from Documents.models import PlanCadastral, PlanLocalisation, CertificatHypotheque, TitreFoncier

class ParcelleSerializer(serializers.Serializer):
    class Meta:
        model = Parcelle
        fields = '__all__'
        
    id = serializers.IntegerField(read_only=True)
    titre = serializers.CharField(max_length=100)
    description = serializers.CharField(allow_blank=True, required=False)
    taille_m2 = serializers.FloatField()
    prix_m2 = serializers.DecimalField(max_digits=12, decimal_places=2)
    localisation = serializers.CharField()
    statut = serializers.ChoiceField(
        choices=[
            ("available", "Disponible"),
            ("sold", "Vendu"),
            ("pending", "En cours")
        ],
        default="available"
    )
    adresse = serializers.CharField(max_length=255, allow_blank=True, required=False)
    type_droit_propriete = serializers.CharField(max_length=100, allow_blank=True, required=False)
    usage = serializers.CharField(max_length=100, allow_blank=True, required=False)
    date_eng = serializers.DateField(read_only=True)
    plan_localisation = serializers.FileField(allow_null=True, required=False)
    last_update = serializers.DateTimeField(read_only=True)
    charge_parcelle = serializers.CharField(allow_blank=True, required=False)
    coordonnees = serializers.CharField(help_text="Liste de coordonnées GeoJSON")
    
    proprietaires_id = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    plan_localisation = serializers.FileField(write_only=True, required=False, allow_null=True)
    titre_foncier = serializers.FileField(write_only=True, required=False, allow_null=True)
    plan_cadastral = serializers.FileField(write_only=True, required=False, allow_null=True)
    certificat_hypotheque = serializers.FileField(write_only=True, required=False, allow_null=True)


    proprietaires = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    def create(self, validated_data):
        validated_data.pop("proprietaires_id", None)

        # Vérifie que les fichiers sont bien fournis à la création
        required_files = ["plan_localisation", "titre_foncier", "plan_cadastral", "certificat_hypotheque"]
        for field in required_files:
            if field not in validated_data:
                raise serializers.ValidationError({field: "Ce fichier est requis pour créer une parcelle."})

        # Création des documents liés
        validated_data["plan_localisation"] = PlanLocalisation.objects.create(doc=validated_data.pop("plan_localisation"))
        validated_data["titre_foncier"] = TitreFoncier.objects.create(doc=validated_data.pop("titre_foncier"))
        validated_data["plan_cadastral"] = PlanCadastral.objects.create(doc=validated_data.pop("plan_cadastral"))
        validated_data["certificat_hypotheque"] = CertificatHypotheque.objects.create(doc=validated_data.pop("certificat_hypotheque"))

        return Parcelle.objects.create(**validated_data)


    def update(self, instance, validated_data):
        validated_data.pop("proprietaires_id", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class TransactionSerializer(serializers.ModelSerializer):
    validations = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def get_validations(self, obj):
        return ValidationSerializer(obj.validations.all(), many=True).data

class ValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validation
        fields = "__all__"
