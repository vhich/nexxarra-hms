from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Clinic
from .validators import phone_validator, numeric_only_validator, allowed_docs_validator

class ClinicSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(validators=[phone_validator])
    license_id = serializers.CharField(validators=[numeric_only_validator, UniqueValidator(
            queryset=Clinic.objects.all(),
            message="This license ID is already used")])
    tax_id = serializers.CharField(validators=[numeric_only_validator, UniqueValidator(
            queryset=Clinic.objects.all(),
            message="This tax ID is already used"
        )])
    proof_of_address = serializers.FileField(validators=[allowed_docs_validator])
    accreditation_certificate = serializers.FileField(validators=[allowed_docs_validator])

    class Meta:
        model = Clinic
        fields = [
            "id",
            "name",
            "email",
            "address",
            "license_id",
            "tax_id",
            "accreditation_certificate",
            "phone",
            "proof_of_address"
        ]

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Clinic name must be at least 3 characters.")
        if Clinic.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("This clinic name is already used")
        return value

    def validate_license_id(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Please provide your valid license id.")
        return value

    def validate_tax_id(self, value):
        if len(value) != 12:
            raise serializers.ValidationError("Please provide your valid tax id.")
        return value

    def validate_email(self, value):
        if Clinic.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already used")
        return value
