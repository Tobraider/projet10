# Generated by Django 4.2.1 on 2023-06-08 07:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_remove_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issues',
            name='assignee_user_id',
            field=models.ForeignKey(default=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auteur_issue', to=settings.AUTH_USER_MODEL), on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL),
        ),
    ]
