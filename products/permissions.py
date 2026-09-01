from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsVendorOrReadonly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        # else for write operations & prevent AnonymousUser
        return request.user.is_authenticated and request.user.role in ["admin", "vendor"]
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # only merchant and requst.user can modify data
        return obj.merchant == request.user

class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, "role", None) == "admin")
        )
