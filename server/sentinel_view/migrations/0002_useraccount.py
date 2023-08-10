# Generated by Django 4.2.4 on 2023-08-10 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentinel_view', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('registered_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
