# Generated by Django 4.2.1 on 2023-06-09 01:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_listing_winner_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=24)),
            ],
        ),
        migrations.RemoveField(
            model_name='listing',
            name='category',
        ),
        migrations.AddField(
            model_name='listing',
            name='category_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='listings', to='auctions.category'),
        ),
    ]