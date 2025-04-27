from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomErrorList
from .models import Pokemon, UserProfile, MarketplaceListing
import random
import requests
import json

def index(request):
    return render(request, 'index.html')

def get_random_pokemon():
    pokemon_id = random.randint(1, 898)
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['name']
    else:
        return None

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            UserProfile.objects.create(user=user, coins=1000)
            pokemon_name = get_random_pokemon()
            if pokemon_name:
                Pokemon.objects.create(name=pokemon_name, user=user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/Signup.html', {'form': form})

@login_required
def collection_view(request):
    user = request.user
    pokemons = user.pokemon_collection.filter(is_listed=False)
    pokemon_data = []
    for pokemon in pokemons:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon.name.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            sprite_url = data['sprites']['front_default']
            types = [t['type']['name'] for t in data['types']]
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
            pokemon_data.append({
                'name': pokemon.name.title(),
                'sprite': sprite_url,
                'types': types,
                'stats': json.dumps(stats)
            })
        else:
            pokemon_data.append({
                'name': pokemon.name.title(),
                'sprite': None,
                'types': [],
                'stats': '{}'
            })
    return render(request, 'collection.html', {'pokemon_data': pokemon_data})

@login_required
def marketplace_view(request):
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('type', '')

    pokemon_data = []

    # Only get Pokémon listed for sale by users
    listings = MarketplaceListing.objects.filter(status='for sale')

    for listing in listings:
        url = f"https://pokeapi.co/api/v2/pokemon/{listing.pokemon.name.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            sprite_url = data['sprites']['front_default']
            types = [t['type']['name'] for t in data['types']]
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}

            # Search & filter
            if search_query and search_query.lower() not in listing.pokemon.name.lower():
                continue
            if filter_type and filter_type not in types:
                continue

            pokemon_data.append({
                'name': listing.pokemon.name.title(),
                'sprite': sprite_url,
                'types': types,
                'price': listing.price,
                'listing_id': listing.id,
                'stats': json.dumps(stats)
            })

    return render(request, 'marketplace.html', {'pokemon_data': pokemon_data})



@login_required
def list_pokemon_view(request):
    user_pokemon = Pokemon.objects.filter(user=request.user, is_listed=False)

    if request.method == 'POST':
        pokemon_id = request.POST.get('pokemon_id')
        price = request.POST.get('price')
        pokemon = Pokemon.objects.get(id=pokemon_id, user=request.user, is_listed=False)

        # Create the listing
        MarketplaceListing.objects.create(pokemon=pokemon, seller=request.user, price=price)

        # Mark as listed instead of deleting
        pokemon.is_listed = True
        pokemon.save()

        return redirect('marketplace')

    return render(request, 'list_pokemon.html', {'user_pokemon': user_pokemon})



@login_required
def buy_pokemon_view(request, listing_id):
    buyer_profile = request.user.userprofile

    if request.method == 'POST':
        listing = MarketplaceListing.objects.get(id=listing_id)
        seller_profile = listing.seller.userprofile

        # Only check for coin balance if buyer and seller are different
        if buyer_profile == seller_profile or buyer_profile.coins >= listing.price:
            if buyer_profile != seller_profile:
                # Transfer coins if buyer and seller are different
                buyer_profile.coins -= listing.price
                seller_profile.coins += listing.price
                seller_profile.save()
                buyer_profile.save()

            # Transfer Pokémon ownership
            pokemon = listing.pokemon
            pokemon.user = request.user
            pokemon.is_listed = False  # Unlist Pokémon
            pokemon.save()

            # Remove the listing
            listing.delete()

            return redirect('collection')
        else:
            return render(request, 'home/error.html', {'message': 'Not enough coins to buy this listed Pokémon.'})
