import re
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import views, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ClinicSerializer, ClinicAdminSerializer, CustomTokenObtainPairSerializer
from .models import Clinic
from .permissions import IsClinicAdminFull, IsClinicAdminLimited


User = get_user_model()

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
    
class ListClinicAdminsView(APIView):
    def get(self, request):
        clinic_admin = User.objects.all()
        serializer = ClinicAdminSerializer(clinic_admin, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SuperAdminClinicDetailView(APIView):
    def get(self, request, clinic_id):
        try:
            clinic = Clinic.objects.get(id=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Clinic not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClinicSerializer(clinic)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RegisterClinicAdminView(APIView):
    def post(self, request):
        serializer = ClinicAdminSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Clinic Admin registered successfully, pending approval",
                "username": user.username,
                "id": user.id,
                "email": user.email,
                "clinic_id": str(user.clinic.id),
                "is_active": user.is_active
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class IsSuperAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == "super_admin"
    
def send_activation_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    activation_link = f"http://127.0.0.1:8000/api/auth/activate/{uidb64}/{token}/"

    clinic_name = user.clinic.name if user.clinic else "your clinic"

    subject = "Activate Your Clinic Admin Account"
    message = (
        f"Hello {user.first_name},\n\n"
        f"You have been registered as a Clinic Admin for {clinic_name}.\n"
        "To activate your account, please click the link below and set up your new password:\n\n"
        f"{activation_link}\n\n"
        "This link will expire after a few days for security reasons.\n"
        "If you did not request this, please ignore this email.\n\n"
        "Best regards,\n"
        "Super Admin Team"
    )

    send_mail(
        subject,
        message,
        "superadmin@Nexxarahms.com",
        ["victoriamglorious@gmail.com"],
        fail_silently=False,
    )

class SendActivationEmailView(APIView):
    # permission_classes = [IsSuperAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id, role="clinic_admin")
        except User.DoesNotExist:
            return Response({"error": "Clinic admin not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"message": "Account is already active"}, status=status.HTTP_200_OK)

        send_activation_email(user)  # 👈 call the helper
        return Response({"message": "Activation email sent successfully"}, status=status.HTTP_200_OK)

class ActivateUserView(views.APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid, role="clinic_admin")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if token_generator.check_token(user, token):
            new_password = request.data.get("password")

            # Advanced password validation
            if not new_password or len(new_password) < 8:
                return Response({"error": "Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)
            if not re.search(r"[A-Z]", new_password):
                return Response({"error": "Password must contain at least one uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
            if not re.search(r"[0-9]", new_password):
                return Response({"error": "Password must contain at least one number"}, status=status.HTTP_400_BAD_REQUEST)
            if not re.search(r"[!@#$%^&*()_\-]", new_password):
                return Response({"error": "Password must contain at least one special character"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.is_active = True
            user.save()
            return Response({"message": "Clinic admin account activated successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

class ResendActivationLinkView(views.APIView):
    # permission_classes = [IsSuperAdmin]
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id, role="clinic_admin")
        except User.DoesNotExist:
            return Response({"error": "Clinic admin not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"message": "Account is already active"}, status=status.HTTP_200_OK)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        activation_link = f"http://127.0.0.1:8000/api/auth/activate/{uidb64}/{token}/"

        clinic_name = user.clinic.name if user.clinic else "your clinic"

        subject = "Resend Activation Link - Clinic Admin Account"
        message = (
            f"Hello {user.first_name},\n\n"
            f"This is a new activation link for your Clinic Admin account at {clinic_name}.\n"
            "Please click the link below to set up your password and activate your account:\n\n"
            f"{activation_link}\n\n"
            "This link will expire after a few days for security reasons.\n"
            "Best regards,\n"
            "Super Admin Team"
        )

        send_mail(
            subject,
            message,
            "superadmin@Nexxarahms.com",
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Activation link resent successfully"}, status=status.HTTP_200_OK)

class ClinicAdminLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ClinicDashboardView(APIView):
    permission_classes = [IsClinicAdminLimited | IsClinicAdminFull]

    def get(self, request):
        return Response({"message": "Welcome to the clinic dashboard"})

# class PatientRecordsView(APIView):
#     permission_classes = [IsClinicAdminFull | IsSuperAdmin]

#     def get(self, request):
#         return Response({"message": "Accessing patient records"})