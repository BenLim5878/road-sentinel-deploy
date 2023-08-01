from django.db import models

class SystemConfiguration(models.Model):
    NUM_IMAGE_THRESHOLD = models.IntegerField(default=10)
    MAP_MAXIMUM_ZOOM_LEVEL = models.IntegerField(default=16)
    MAP_MINIMUM_ZOOM_LEVEL = models.IntegerField(default=6)
    MAP_INITIAL_ZOOM_LEVEL = models.IntegerField(default=7)
