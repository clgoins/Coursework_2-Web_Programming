# Generated by Django 4.2.1 on 2023-06-06 01:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_bid_listing_id_alter_bid_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='listing_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.listing'),
        ),
    ]
