from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.db.models import Q


class IsUserExists(permissions.BasePermission):

    def has_permission(self, request, view):
        if get_user_model().objects.filter(Q(id=view.kwargs['pk']) & Q(is_active=True)).count() > 0:
            return True
        else:
            self.message = 'Unauthorized operations'
            return False


class UserObjectPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user.id == request.user.id:
            return True
        else:
            return False
