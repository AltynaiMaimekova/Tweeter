# Generated by Django 3.2 on 2022-09-15 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together={('followed', 'follower')},
        ),
    ]
