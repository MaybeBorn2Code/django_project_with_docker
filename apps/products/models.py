from django.db import models

# Create your models here.


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    image = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = (
            "-id",
        )
        verbose_name = "product"
        verbose_name_plural = "products"
