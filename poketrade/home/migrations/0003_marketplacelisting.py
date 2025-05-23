# Generated by Django 5.2 on 2025-04-26 21:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketplaceListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
                ('status', models.CharField(choices=[('for sale', 'For Sale'), ('for trade', 'For Trade')], default='for sale', max_length=10)),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listing', to='home.pokemon')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
