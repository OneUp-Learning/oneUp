# Generated by Django 2.1.2 on 2022-01-10 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0115_auto_20220109_2353'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StudentAvatar',
            new_name='StudentCustomAvatar',
        ),
    ]
