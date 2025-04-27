from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import signup_view, marketplace_view, list_pokemon_view, buy_pokemon_view

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('collection/', views.collection_view, name='collection'),
    path('marketplace/', marketplace_view, name='marketplace'),
    path('marketplace/list/', views.list_marketplace_view, name='list_marketplace'),
    path('marketplace/list/', list_pokemon_view, name='list_pokemon'),
    path('marketplace/buy/<int:listing_id>/', buy_pokemon_view, name='buy_pokemon'),
    path('marketplace/propose-trade/<int:listing_id>/', views.propose_trade_view, name='propose_trade'),
    path('my-trade-offers/', views.my_trade_offers_view, name='my_trade_offers'),
    path('trade-offer/<int:offer_id>/<str:action>/', views.handle_trade_offer_view, name='handle_trade_offer'),
    path('my-trade-notifications/', views.my_trade_notifications_view, name='my_trade_notifications'),
    path('revoke-listing/<int:listing_id>/', views.revoke_listing_view, name='revoke_listing'),
]
