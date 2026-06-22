from rest_framework import serializers
from .models import Clinic

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        # Explicitly define what goes out to the frontend
        fields = ['id', 'name', 'address', 'phone', 'email', 'accreditation_certificate', 'proof_of_address', 'created_at', 'is_active']
