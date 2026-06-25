from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.crypto import get_random_string

from rest_framework import viewsets, views, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ClinicSerializer

from .models import Clinic

from .services import create_user

class RegisterClinicView(APIView):
    def post(self, request):
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            clinic = serializer.save()
            return Response({
                "message": "Clinic registered successfully!",
                "clinic_id": str(clinic.id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListClinicsView(APIView):
    def get(self, request):
        clinics = Clinic.objects.all()
        serializer = ClinicSerializer(clinics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class ActivateUserView(views.APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if token_generator.check_token(user, token):
            new_password = request.data.get("password")
            user.set_password(new_password)
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
    
class RegisterClinicAdminView(APIView):
    def post(self, request):
        username = request.data.get("username")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        phone=request.data.get("phone")
        clinic_id = request.data.get("clinic_id")

        try:
            clinic = Clinic.objects.get(id=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Invalid clinic ID"}, status=status.HTTP_404_NOT_FOUND)
        
        random_password = get_random_string(12)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=random_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role="clinic_admin",
            clinic=clinic,
            is_active=False,
        )

        return Response({
            "message": "Clinic Admin registered successfully, pending approval",
            "username": user.username,
            "user_id": user.id,
            "password": user.password,
            "email": user.email,
            "clinic_id": str(clinic.id),
            "is_active": user.is_active,
        }, status=status.HTTP_201_CREATED)
