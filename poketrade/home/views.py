from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required  # <- added this
from .forms import CustomUserCreationForm, CustomErrorList
from .models import Pokemon
import random
import requests

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
            auth_login(request, user)  # Log the user in after successful signup

            # Fetch random Pokémon and assign it
            pokemon_name = get_random_pokemon()
            print(pokemon_name)
            if pokemon_name:
                Pokemon.objects.create(name=pokemon_name, user=user)

            return redirect('index')  # Redirect to the home page
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/Signup.html', {'form': form})

def login_view(request):
    template_data = {'title': 'Login'}

    if request.method == 'GET':
        return render(request, 'accounts/Login.html', {'template_data': template_data})

    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/Login.html', {'template_data': template_data})

        else:
            auth_login(request, user)
            return redirect('index')

# --- NEW ---
@login_required
def collection_view(request):
    user = request.user
    pokemons = user.pokemon_collection.all()

    pokemon_data = []

    for pokemon in pokemons:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon.name.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            sprite_url = data['sprites']['front_default']  # main image
            types = [t['type']['name'] for t in data['types']]  # list of types
            pokemon_data.append({
                'name': pokemon.name.title(),
                'sprite': sprite_url,
                'types': types
            })
        else:
            # fallback if API call fails
            pokemon_data.append({
                'name': pokemon.name.title(),
                'sprite': None,
                'types': []
            })

    return render(request, 'collection.html', {'pokemon_data': pokemon_data})
