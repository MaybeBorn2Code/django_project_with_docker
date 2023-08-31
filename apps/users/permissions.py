# DRF
from rest_framework import permissions
# local
from .serializers import UserSerializer


class ViewPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        data = UserSerializer(request.data).data

        view_access = any(
            p['name'] == 'view_' + view.permission_object for p in data['role']['permission'])
        edit_access = any(
            p['name'] == 'edit_' + view.permission_object for p in data['role']['permission'])

        if request.method == "GET":
            return view_access or edit_access

        return edit_access
