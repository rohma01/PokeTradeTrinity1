# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Pokemon(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pokemon_collection')
    is_listed = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} owned by {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=1000)

    def __str__(self):
        return f"{self.user.username} Profile"

class MarketplaceListing(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='listing')
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    status = models.CharField(max_length=10, choices=[('for sale', 'For Sale'), ('for trade', 'For Trade')], default='for sale')

    def __str__(self):
        return f"{self.pokemon.name} by {self.seller.username} - {self.status} ({self.price} coins)"
