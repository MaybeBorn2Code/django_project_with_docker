# Django
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    name = models.CharField(max_length=200)


class Role(models.Model):
    name = models.CharField(max_length=200)
    permission = models.ManyToManyField(Permission)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Users(AbstractUser):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = (
            "-id",
        )
        verbose_name = "user"
        verbose_name_plural = "users"
