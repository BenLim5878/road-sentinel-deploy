from django.db import models

class ImageAnnotation(models.Model):
    uuid = models.OneToOneField('UserImage', on_delete=models.CASCADE, primary_key=True, unique=True)
    processTimestamp = models.DateTimeField()
    numPothole = models.IntegerField()
    isAcknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f'{str(self.uuid)}, {str(self.processTimestamp)},{str(self.numPothole)},{str(self.isAcknowledged)}'
    
class GeoLocationGoogle(models.Model):
    uuid = models.OneToOneField('UserImage', on_delete=models.CASCADE, primary_key=True, unique=True)
    streetNumber = models.CharField(max_length=100)
    postalCode = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.streetNumber}, {self.postalCode}, {self.city}, {self.state}, {self.country}'
    
class UserImage(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    entryDate = models.DateTimeField()
    def __str__(self):
        return self.uuid

