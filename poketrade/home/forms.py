from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe
from .models import Pokemon, MarketplaceListing

class CustomErrorList(forms.utils.ErrorList):
    def as_ul(self):
        return mark_safe(''.join([f'<li class="text-red-500">{e}</li>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class MarketplaceListingForm(forms.ModelForm):
    price = forms.IntegerField(required=False, min_value=1, label="Sell for (coins)", widget=forms.NumberInput(attrs={'placeholder': 'e.g. 100'}))
    desired_pokemon_names = forms.CharField(
        required=False,
        label="Willing to trade for (comma-separated Pokémon names)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Pikachu, Bulbasaur'}),
        help_text="Enter names of Pokémon you want in exchange. Leave blank if only selling."
    )

    class Meta:
        model = MarketplaceListing
        fields = ['pokemon', 'price', 'desired_pokemon_names']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['pokemon'].queryset = Pokemon.objects.filter(user=user, is_listed=False)

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        desired = cleaned_data.get('desired_pokemon_names')
        if not price and not desired:
            raise forms.ValidationError("You must specify a price or desired Pokémon (or both).")
        return cleaned_data