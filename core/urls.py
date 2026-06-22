from rest_framework import routers
from .views import ClinicViewSet, ActivateUserView, CreateClinicAdminView

from django.urls import path

router = routers.DefaultRouter()
router.register(r'clinics', ClinicViewSet)
urlpatterns = [
    path('auth/activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('auth/create-clinic-admin/', CreateClinicAdminView.as_view(), name='create-clinic-admin'),
]

urlpatterns = urlpatterns + router.urls
