# Generated by Django 4.2.1 on 2023-06-14 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_alter_issues_assignee_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='description',
            field=models.TextField(max_length=2048),
        ),
    ]
