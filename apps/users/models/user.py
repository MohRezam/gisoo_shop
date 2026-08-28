from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _

from apps.users.managers.managers import UserManager
from core_gisoo_backend.storage_backends.locations import avatar_path


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        verbose_name=_("phone_number"),
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("email"),
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("first_name"),
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("last_name"),
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("is_staff"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("active"),
    )
    birthdate = models.DateField(verbose_name=_("birthdate"), null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created_at"),
    )
    avatar = models.ImageField(
        upload_to=avatar_path(),
        verbose_name=_("avatar"),
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.phone_number
