from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

class StaffAuthBackend(ModelBackend):
    def user_can_authenticate(self, user):
        if not super().user_can_authenticate(user):
            return False
        if hasattr(user, 'StaffProfile') and not user.StaffProfile.is_active:
            raise PermissionDenied("Your account has been deactivated by the clinic admin.")
        return True
