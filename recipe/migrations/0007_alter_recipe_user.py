# Generated by Django 5.1 on 2025-03-22 08:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0006_alter_comment_recipe'),
        ('users', '0004_rolechangerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userprofile'),
        ),
    ]
