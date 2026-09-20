from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from apps.users.managers.managers import UserManager
from core_gisoo_backend.storage_backends.locations import avatar_path


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="شماره تلفن",
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="ایمیل",
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام",
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام خانوادگی",
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="کارمند",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    birthdate = models.DateField(verbose_name=_("birthdate"), null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    avatar = models.ImageField(
        upload_to=avatar_path(),
        verbose_name="تصویر پروفایل",
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.phone_number
