# Generated by Django 4.2.1 on 2023-06-24 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_alter_post_timestamp_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post',
            field=models.TextField(max_length=400),
        ),
    ]
