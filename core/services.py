from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(username, email, first_name, last_name, password, role, phone, clinic=None, is_active=False):
    user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        phone=phone,
        role=role,
        clinic=clinic,
        is_active=is_active
    )
    return user
