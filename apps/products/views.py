# Django
from django.core.files.storage import default_storage

# DRF
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin
)

# Local
from .models import Product
from .serializers import ProductSerializer
from settings.pagination import CustomPagination
from users.authentication import JWTAuthentication


class ProductGenericAPIView(
    GenericAPIView,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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
        return Response(
            {
                'data': self.create(request).data
            }
        )

    def put(self, request, pk=None):
        return Response(
            {
                'data': self.partial_update(request, pk).data
            }
        )

    def delete(self, request, pk=None):
        return self.destroy(request, pk)


class FileUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, )

    def post(self, request):
        file = request.FILES['image']
        file_name = default_storage.save(file.name, file)
        url = default_storage.url(file_name)

        return Response(
            {
                'url': "http://localhost:8000/api" + url
            }
        )
