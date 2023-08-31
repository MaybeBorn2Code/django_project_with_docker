# Python
import csv
import psycopg2
# Django
from django.shortcuts import render
from django.http.response import HttpResponse
# DRF
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin
)
# local
from .models import Order, OrderItem
from .serializers import OrderSerializer
from settings.pagination import CustomPagination
from users.authentication import JWTAuthentication
from settings.base import DATABASES


class OrderGenericAPIView(
    GenericAPIView,
    ListModelMixin,
    RetrieveModelMixin
):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        if pk:
            return Response(
                {
                    'data': self.retrieve(request, pk).data
                }
            )
        return self.list(request)


class ExportAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=orders.csv'

        orders = Order.objects.all()
        writer = csv.writer(response)

        writer.writerow(
            ['ID', 'Name', 'Email', 'Product Title', 'Price', 'Quantity'])

        for order in orders:
            writer.writerow(
                [order.id, order.name, order.email, '', '', ''])
            orderItems = OrderItem.objects.all().filter(order_id=order.id)

            for item in orderItems:
                writer.writerow(
                    ['', '', '', item.product_title, item.price, item.quantity])

        return response


class ChartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _):
        db_config = DATABASES["default"]

        with psycopg2.connect(
            dbname=db_config["NAME"],
            user=db_config["USER"],
            password=db_config["PASSWORD"],
            host=db_config["HOST"],
            port=db_config["PORT"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT DATE_TRUNC('day', o.created_at) as date, sum(i.quantity * i.price) as sum
                    FROM orders_order as o
                    JOIN orders_orderitem as i ON o.id = i.order_id
                    GROUP BY date
                    """
                )
                rows = cursor.fetchall()

            data = [
                {
                    'data': result[0],
                    'sum': result[1]} for result in rows

            ]

        return Response(
            {
                'data': data
            }
        )
