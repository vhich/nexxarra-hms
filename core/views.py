from django.shortcuts import render
from rest_framework import viewsets
from .models import Clinic
from .serializers import ClinicSerializer

class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all_objects()  # include verified/unverified clinics
    serializer_class = ClinicSerializer