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
    price = models.IntegerField(null=True, blank=True)
    desired_pokemon_names = models.CharField(max_length=300, blank=True, help_text='Comma-separated names of Pokémon the owner wants')
    status = models.CharField(max_length=10, choices=[('for sale', 'For Sale'), ('for trade', 'For Trade'), ('for both', 'For Both')], default='for sale')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def desired_pokemon_list(self):
        return [name.strip().lower() for name in self.desired_pokemon_names.split(',') if name.strip()]

    def __str__(self):
        details = []
        if self.price:
            details.append(f"{self.price} coins")
        if self.desired_pokemon_names:
            details.append(f"for {self.desired_pokemon_names}")
        return f"{self.pokemon.name} by {self.seller.username} - {' or '.join(details) if details else 'No offer'}"

class TradeOffer(models.Model):
    listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name='offers')
    offered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trade_offers')
    pokemon_offered = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='trade_pokemon_offered')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_result_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Offer by {self.offered_by.username} with {self.pokemon_offered.name} for listing {self.listing.id} ({self.status})"
