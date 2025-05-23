# Generated by Django 5.1.5 on 2025-04-27 15:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_pokemon_is_listed'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desired_pokemon_names', models.CharField(help_text='Comma-separated names of Pokémon the owner wants', max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('offered_pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_offered', to='home.pokemon')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TradeOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='home.tradelisting')),
                ('offered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_offers', to=settings.AUTH_USER_MODEL)),
                ('pokemon_offered', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_pokemon_offered', to='home.pokemon')),
            ],
        ),
    ]
