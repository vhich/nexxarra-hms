from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(username, email, random_password, role, phone, clinic=None, is_active=False):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=random_password,
        phone=phone,
        role=role,
        clinic=clinic,
        is_active=is_active
    )
    return user
