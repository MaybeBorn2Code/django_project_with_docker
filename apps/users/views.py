# Django
from django.shortcuts import render
# DRF
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin
)
# Local
from .serializers import (
    UserSerializer,
    PermissionSerializer,
    RoleSerializer
)
from .models import Users, Permission, Role
from .authentication import generate_access_token, JWTAuthentication
from settings.pagination import CustomPagination
from .permissions import ViewPermissions


@api_view(['POST'])
def register(request):
    data = request.data

    if data['password'] != data['password_confirm']:
        raise exceptions.APIException('Passwords do not match!')

    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = Users.objects.filter(email=email).first()

    if user is None:
        raise exceptions.AuthenticationFailed("User not found!")

    if not user.check_password(password):
        raise exceptions.AuthenticationFailed('Incorrect password')

    response = Response()

    token = generate_access_token(user)
    response.set_cookie(key='jwt', value=token, httponly=True)

    response.data = {
        "jwt": token
    }
    return response


@api_view(['POST'])
def logout(request):
    response = Response()
    response.delete_cookie(key='jwt')
    response.data = {
        'message': 'Success'
    }
    return response


# @api_view(['GET'])
# def users(request):
#     serializer = UserSerializer(Users.objects.all(), many=True)
#     return Response(serializer.data)


class AuthenticatedUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        data['permission'] = [p['name'] for p in data['role']['permission']]

        return Response({
            'data': data
        })


class PermissionAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PermissionSerializer(Permission.objects.all(), many=True)

        return Response(
            {
                'data': serializer.data
            }
        )


class RolesViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_object = 'roles'

    def list(self, request):
        serializer = RoleSerializer(Role.objects.all(), many=True)
        return Response(
            {
                'data': serializer.data
            }
        )

    def create(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'data': serializer.data
            }, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        role = Role.objects.get(id=pk)
        serializer = RoleSerializer(role)
        return Response(
            {
                'data': serializer.data
            }
        )

    def update(self, request, pk=None):
        role = Role.objects.get(id=pk)
        serializer = RoleSerializer(instance=role, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'data': serializer.data
            }, status=status.HTTP_202_ACCEPTED
        )

    def destroy(self, request, pk=None):
        role = Role.objects.get(id=pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGenericAPIView(
    GenericAPIView,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Users.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        if pk:
            return Response(
                {
                    'data': self.retrieve(request, pk).data
                }
            )
        return self.list(request)

    def post(self, request):
        request.data.update(
            {
                'password': 'root',
                'role': request.data['role_id']
            }
        )
        return Response(
            {
                'data': self.create(request).data
            }
        )

    def put(self, request, pk=None):

        if request.data['role_id']:
            request.data.update(
                {
                    'role': request.data['role_id']
                }
            )
        return Response(
            {
                'data': self.partial_update(request, pk).data
            }
        )

    def delete(self, request, pk=None):
        return self.destroy(request, pk)


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        if request.data['password'] != request.data['password_confirm']:
            raise exceptions.ValidationError('Passwords do not match')
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
