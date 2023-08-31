# Django
from django.urls import path
# Local
from .views import (
    register,
    login,
    logout,
    AuthenticatedUser,
    PermissionAPIView,
    RolesViewSet,
    UserGenericAPIView,
    ProfileInfoAPIView,
    ProfilePasswordAPIView
)

urlpatterns = [
    path('register', register),
    path('login', login),
    path('logout', logout),
    path('user', AuthenticatedUser.as_view()),
    path('permissions', PermissionAPIView.as_view()),
    path('roles', RolesViewSet.as_view(
        {
            'get': 'list',
            'post': 'create'
        }
    )),
    path('roles/<str:pk>', RolesViewSet.as_view(
        {
            'get': 'retrieve',
            'put': 'update',
            'delete': 'destroy'
        }
    )),
    path('users/info', ProfileInfoAPIView.as_view()),
    path('users/password', ProfilePasswordAPIView.as_view()),
    path('users', UserGenericAPIView.as_view()),
    path('users/<str:pk>', UserGenericAPIView.as_view()),

]
