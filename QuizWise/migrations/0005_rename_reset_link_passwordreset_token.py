# Generated by Django 4.2.7 on 2023-11-26 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('QuizWise', '0004_passwordreset'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passwordreset',
            old_name='reset_link',
            new_name='token',
        ),
    ]