# Generated by Django 4.2.3 on 2023-07-16 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserImage',
            fields=[
                ('uuid', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('entryDate', models.DateTimeField()),
                ('latitude', models.CharField(max_length=255)),
                ('longitude', models.CharField(max_length=255)),
            ],
        ),
    ]
