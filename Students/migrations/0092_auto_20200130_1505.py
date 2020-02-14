# Generated by Django 2.0.8 on 2020-01-30 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0091_duelchallenges_hasexpired'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentvirtualcurrencytransactions',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='timestamp'),
        ),
        migrations.AddField(
            model_name='studentvirtualcurrencytransactions',
            name='transactionReason',
            field=models.CharField(default='', max_length=600),
        ),
    ]