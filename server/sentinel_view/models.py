from django.db import models

class SystemConfiguration(models.Model):
    NUM_IMAGE_THRESHOLD = models.IntegerField(default=10)
    MAP_MAXIMUM_ZOOM_LEVEL = models.IntegerField(default=16)
    MAP_MINIMUM_ZOOM_LEVEL = models.IntegerField(default=6)
    MAP_INITIAL_ZOOM_LEVEL = models.IntegerField(default=7)

class UserAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    registered_date = models.DateTimeField(auto_now_add=True)