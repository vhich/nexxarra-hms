from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from rest_framework import viewsets, views, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ClinicSerializer

from .models import Clinic

from .services import create_clinic_admin

class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all_objects()  # include verified/unverified clinics
    serializer_class = ClinicSerializer


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


class CreateClinicAdminView(APIView):
    def post(self, request):
        email = request.data.get("email")
        clinic_id = request.data.get("clinic_id")

        if not email or not clinic_id:
            return Response({"error": "Email and clinic_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clinic = Clinic.objects.get(id=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Clinic not found"}, status=status.HTTP_404_NOT_FOUND)

        user = create_clinic_admin(email, clinic)

        return Response({
            "message": "Clinic admin created successfully",
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "clinic_id": clinic_id,
        }, status=status.HTTP_201_CREATED)