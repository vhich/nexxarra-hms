from rest_framework import serializers
from .models import Clinic

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        # Explicitly define what goes out to the frontend
        fields = '__all__'
