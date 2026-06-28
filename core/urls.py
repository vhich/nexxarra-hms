
from .views import ActivateUserView, ResendActivationLinkView, SendActivationEmailView, ListClinicsView, ListClinicAdminsView, SuperAdminClinicDetailView, RegisterClinicAdminView, RegisterClinicView, ClinicAdminLoginView

from django.urls import path

# router = routers.DefaultRouter()
urlpatterns = [
    path('auth/register-clinic/', RegisterClinicView.as_view(), name='register-clinic'),
    path('auth/register-clinic-admin/', RegisterClinicAdminView.as_view(), name='register-clinic-admin'),

    path('clinics/', ListClinicsView.as_view(), name='list-clinics'),
    path('clinic-admins/', ListClinicAdminsView.as_view(), name='list-clinic-admins'),
    path("clinic/<uuid:clinic_id>/", SuperAdminClinicDetailView.as_view(), name="single-clinic-details"),

    path("auth/send/activate/<int:user_id>/", SendActivationEmailView.as_view(), name="send-activation-email"),
    path("auth/resend/activate/<int:user_id>/", ResendActivationLinkView.as_view(), name="resend-activation-link"),
    path("auth/activate/<uidb64>/<token>/", ActivateUserView.as_view(), name="activate-user"),

    path("auth/clinic-admin/login/", ClinicAdminLoginView.as_view(), name="clinic-admin-login"),
]

urlpatterns = urlpatterns