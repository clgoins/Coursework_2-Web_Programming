# Generated by Django 4.2.1 on 2023-06-08 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_watchlist_listing_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='winner_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wonListings', to=settings.AUTH_USER_MODEL),
        ),
    ]