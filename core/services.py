from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

def create_clinic_admin(email, clinic):
    random_password = get_random_string(12)
    user = User.objects.create_user(
        username=email,
        email=email,
        password=random_password,
        role="clinic_admin",
        clinic=clinic,
        is_active=False
    )
    return user
