from django.db import models
from users.models import CustomUser
from django.contrib.auth.models import AbstractUser
from django import forms

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

