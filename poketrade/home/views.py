from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomErrorList, MarketplaceListingForm
from .models import Pokemon, UserProfile, MarketplaceListing, TradeOffer
import random
import requests
import json
from django import forms
from django.contrib import messages

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
    user = request.user
    listings = MarketplaceListing.objects.filter(pokemon__is_listed=True).select_related('pokemon', 'seller')
    pokemon_data = []
    user_pokemon_names = set(p.name.lower() for p in user.pokemon_collection.all()) if user.is_authenticated else set()
    for listing in listings:
        url = f"https://pokeapi.co/api/v2/pokemon/{listing.pokemon.name.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            sprite_url = data['sprites']['front_default']
            types = [t['type']['name'] for t in data['types']]
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        else:
            sprite_url = None
            types = []
            stats = {}
        # Determine eligibility for trade
        desired_list = listing.desired_pokemon_list()
        has_desired = bool(user_pokemon_names.intersection(desired_list)) if desired_list else False
        pokemon_data.append({
            'name': listing.pokemon.name.title(),
            'sprite': sprite_url,
            'types': types,
            'stats': json.dumps(stats),
            'price': listing.price,
            'desired_pokemon_names': listing.desired_pokemon_names,
            'has_desired': has_desired,
            'listing_id': listing.id,
            'seller': listing.seller,
            'can_buy': listing.price is not None,
            'can_trade': bool(desired_list),
            'is_owner': listing.seller == user,
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

@login_required
def list_marketplace_view(request):
    user = request.user
    if request.method == 'POST':
        form = MarketplaceListingForm(request.POST, user=user)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = user
            listing.status = (
                'for both' if listing.price and listing.desired_pokemon_names else
                'for sale' if listing.price else 'for trade'
            )
            listing.save()
            # Mark the Pokémon as listed
            listing.pokemon.is_listed = True
            listing.pokemon.save()
            return redirect('collection')
    else:
        form = MarketplaceListingForm(user=user)
    return render(request, 'list_marketplace.html', {'form': form})

@login_required
def propose_trade_view(request, listing_id):
    user = request.user
    listing = MarketplaceListing.objects.get(id=listing_id)
    if listing.seller == user:
        return render(request, 'home/error.html', {'message': 'You cannot propose a trade for your own listing.'})
    eligible_pokemon = user.pokemon_collection.filter(is_listed=False, name__in=listing.desired_pokemon_list())
    if not eligible_pokemon:
        return render(request, 'home/error.html', {'message': 'You do not have any Pokémon that the seller wants.'})
    class OfferForm(forms.Form):
        pokemon = forms.ModelChoiceField(queryset=eligible_pokemon, label="Select Pokémon to Offer")
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            trade_offer = TradeOffer.objects.create(
                listing=listing,
                offered_by=user,
                pokemon_offered=form.cleaned_data['pokemon'],
                status='pending',
            )
            trade_offer.pokemon_offered.is_listed = True
            trade_offer.pokemon_offered.save()
            messages.success(request, f"Trade offer submitted! The seller ({listing.seller.username}) will see your offer in 'My Trade Offers'.")
            return render(request, 'home/success.html', {'message': 'Trade offer submitted!'})
    else:
        form = OfferForm()
    return render(request, 'propose_trade.html', {'form': form, 'listing': listing})

@login_required
def my_trade_offers_view(request):
    user = request.user
    my_listings = MarketplaceListing.objects.filter(seller=user)
    offers = []
    for listing in my_listings:
        for offer in listing.offers.all():
            offers.append({
                'offer': offer,
                'listing': listing,
                'offered_by': offer.offered_by,
                'pokemon_offered': offer.pokemon_offered,
            })
    if not offers:
        messages.info(request, "You have no incoming trade offers yet. When someone proposes a trade, it will appear here!")
    return render(request, 'my_trade_offers.html', {'offers': offers})

@login_required
def my_trade_notifications_view(request):
    user = request.user
    my_offers = TradeOffer.objects.filter(offered_by=user).select_related('listing', 'pokemon_offered')
    notifications = []
    unread_ids = []
    for offer in my_offers.order_by('-created_at'):
        if offer.status == 'accepted':
            notifications.append({
                'type': 'accepted',
                'listing': offer.listing,
                'pokemon_offered': offer.pokemon_offered,
                'accepted_at': offer.created_at,
                'is_result_read': offer.is_result_read,
            })
            if not offer.is_result_read:
                unread_ids.append(offer.id)
        elif offer.status == 'rejected':
            notifications.append({
                'type': 'rejected',
                'listing': offer.listing,
                'pokemon_offered': offer.pokemon_offered,
                'rejected_at': offer.created_at,
                'is_result_read': offer.is_result_read,
            })
            if not offer.is_result_read:
                unread_ids.append(offer.id)
    # Mark all unread as read
    if unread_ids:
        TradeOffer.objects.filter(id__in=unread_ids).update(is_result_read=True)
    return render(request, 'my_trade_notifications.html', {'notifications': notifications})

@login_required
def handle_trade_offer_view(request, offer_id, action):
    user = request.user
    offer = TradeOffer.objects.select_related('listing', 'pokemon_offered', 'offered_by').get(id=offer_id)
    listing = offer.listing
    if listing.seller != user:
        return render(request, 'home/error.html', {'message': 'You are not authorized to handle this offer.'})
    if offer.status != 'pending':
        return render(request, 'home/error.html', {'message': 'This offer has already been handled.'})
    if action == 'accept':
        offered_pokemon = offer.pokemon_offered
        seller_pokemon = listing.pokemon
        buyer = offer.offered_by
        offered_pokemon.user, seller_pokemon.user = seller_pokemon.user, offered_pokemon.user
        offered_pokemon.is_listed = False
        seller_pokemon.is_listed = False
        offered_pokemon.save()
        seller_pokemon.save()
        offer.status = 'accepted'
        offer.save()
        # Get all other offers BEFORE deleting the listing
        other_offers = list(listing.offers.exclude(id=offer.id))
        # Delete listing BEFORE updating other offers to avoid ValueError
        listing.delete()
        for other_offer in other_offers:
            other_offer.status = 'rejected'
            other_offer.pokemon_offered.is_listed = False
            other_offer.pokemon_offered.save()
            try:
                other_offer.save()
            except Exception:
                pass  # If the row is already deleted due to cascade, ignore
        messages.success(request, f"Trade accepted! Pokémon have been swapped.")
        return render(request, 'home/success.html', {'message': 'Trade accepted and Pokémon swapped!'})
    elif action == 'reject':
        offer.status = 'rejected'
        offer.pokemon_offered.is_listed = False
        offer.pokemon_offered.save()
        offer.save()
        messages.info(request, "Trade offer rejected.")
        return render(request, 'home/success.html', {'message': 'Trade offer rejected.'})
    else:
        return render(request, 'home/error.html', {'message': 'Invalid action.'})

@login_required
def revoke_listing_view(request, listing_id):
    user = request.user
    try:
        listing = MarketplaceListing.objects.get(id=listing_id, seller=user)
    except MarketplaceListing.DoesNotExist:
        return render(request, 'home/error.html', {'message': 'Listing not found or not owned by you.'})
    if request.method == 'POST':
        pokemon = listing.pokemon
        pokemon.is_listed = False
        pokemon.save()
        listing.delete()
        messages.success(request, 'Your listing has been revoked and your Pokémon is no longer listed.')
        return redirect('marketplace')
    return render(request, 'home/error.html', {'message': 'Invalid request.'})

def base_context(request):
    notif_count = 0
    if request.user.is_authenticated:
        from .models import MarketplaceListing, TradeOffer
        notif_count = TradeOffer.objects.filter(listing__seller=request.user, status='pending').count()
    return {'trade_offer_notif_count': notif_count}
