# Generated by Django 5.1 on 2025-03-23 07:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0008_alter_recipe_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='recipe.recipe'),
        ),
    ]
