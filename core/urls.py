from rest_framework import routers
from .views import ActivateUserView,ListClinicsView, RegisterClinicAdminView, RegisterClinicView

from django.urls import path

# router = routers.DefaultRouter()
urlpatterns = [
    path('auth/activate/<uidb64>/<token>', ActivateUserView.as_view(), name='activate'),
    path('auth/register-clinic-admin', RegisterClinicAdminView.as_view(), name='register-clinic-admin'),
    path('auth/register-clinic', RegisterClinicView.as_view(), name='register-clinic'),
    path('clinics', ListClinicsView.as_view(), name='list-clinics'),
    # path('auth/create-clinic-admin/', CreateClinicAdminView.as_view(), name='create-clinic-admin'),
]

urlpatterns = urlpatterns
