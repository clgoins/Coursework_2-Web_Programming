# Generated by Django 4.2.1 on 2023-06-24 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_alter_post_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post',
            field=models.TextField(max_length=500),
        ),
    ]
