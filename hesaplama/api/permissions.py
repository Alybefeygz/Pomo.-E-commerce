from rest_framework import permissions

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Sadece süper kullanıcıların düzenleme yapmasına izin veren permission sınıfı.
    """
    def has_permission(self, request, view):
        # GET, HEAD veya OPTIONS istekleri için izin ver
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Diğer istekler için sadece süper kullanıcılara izin ver
        return request.user.is_superuser 