from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.db import models


class Role(models.TextChoices):
    TENANT = "TENANT", ('Người thuê')
    ADMIN = 'ADMIN', ('Quản trị viên')
    HOST = 'HOST', ('Chủ nhà')


class User(AbstractUser):
    avatar = CloudinaryField('avatar')
    role = models.CharField(max_length=6, choices=Role.choices, null=False)