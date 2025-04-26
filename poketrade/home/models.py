# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Pokemon(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pokemon_collection')

    def __str__(self):
        return f"{self.name} owned by {self.user.username}"

