# Generated by Django 4.2.1 on 2023-06-24 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_alter_post_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='fmtTime',
            field=models.CharField(default=0, max_length=24),
            preserve_default=False,
        ),
    ]
