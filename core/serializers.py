from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

from .models import Clinic, User
from .validators import phone_validator, numeric_only_validator, allowed_docs_validator

from django.contrib.auth import get_user_model, authenticate
from django.utils.crypto import get_random_string

class ClinicAdminNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "is_active", "feature_access_level"]


class ClinicSerializer(serializers.ModelSerializer):
    clinic_admin = serializers.SerializerMethodField()
    phone = serializers.CharField(validators=[phone_validator])
    license_id = serializers.CharField(validators=[numeric_only_validator, UniqueValidator(
            queryset=Clinic.objects.all(),
            message="Invalid license ID")])
    tax_id = serializers.CharField(validators=[numeric_only_validator, UniqueValidator(
            queryset=Clinic.objects.all(),
            message="Invalid tax ID"
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
            "proof_of_address",
            "status",
            "clinic_admin"
        ]

    def get_clinic_admin(self, obj):
        admin = User.objects.filter(clinic=obj, role="clinic_admin").first()
        if admin:
            return ClinicAdminNestedSerializer(admin).data
        return None

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
            raise serializers.ValidationError("invalid email address")
        return value
    

User = get_user_model()

class ClinicAdminSerializer(serializers.ModelSerializer):
    clinic_id = serializers.UUIDField(write_only=True)
    phone = serializers.CharField(validators=[phone_validator])
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "clinic_id",
            "feature_access_level"
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("invalid email address")
        return value

    def validate_clinic_id(self, value):
        try:
            Clinic.objects.get(id=value)
        except Clinic.DoesNotExist:
            raise serializers.ValidationError("Invalid clinic ID")
        
        if User.objects.filter(clinic_id=value, role="clinic_admin").exists():
            raise serializers.ValidationError("This clinic already has an admin")

        return value
    
    def validate_first_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters")
        return value

    def validate_last_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters")
        return value       

    def create(self, validated_data):
        clinic_id = validated_data.pop("clinic_id")
        clinic = Clinic.objects.get(id=clinic_id)

        random_password = get_random_string(12)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            role="clinic_admin",
            clinic=clinic,
            password=random_password,
            feature_access_level="limited",
            is_active=False
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "invalid_credentials": "Invalid username or password.",
        "inactive_account": "Your account is not active. Please activate via the email link."
    }

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed(self.error_messages["invalid_credentials"])

        if not user.is_active:
            raise AuthenticationFailed(self.error_messages["inactive_account"])
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed(self.error_messages["invalid_credentials"])

        data = super().validate(attrs)

        # Add custom claims
        data["role"] = self.user.role
        data["feature_access_level"] = self.user.feature_access_level
        return data
