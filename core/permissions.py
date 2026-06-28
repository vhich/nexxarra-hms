from rest_framework.permissions import BasePermission

class IsClinicAdminLimited(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.auth.get("role") == "clinic_admin" and
            request.auth.get("feature_access_level") == "limited"
        )

class IsClinicAdminFull(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.auth.get("role") == "clinic_admin" and
            request.auth.get("feature_access_level") == "full_access"
        )

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.auth.get("role") == "super_admin"
        )
