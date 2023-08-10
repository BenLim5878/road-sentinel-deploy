from django.shortcuts import render
import requests
from django.http import JsonResponse,HttpResponse,HttpResponseNotFound
from django.contrib.auth.models import User
from django.conf import settings

def process_latlong(request):
    if (settings.DEBUG):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        address_components = get_address(lat, lng)
        return JsonResponse(address_components)
    else:
        return HttpResponseNotFound()
    
    
def get_address(latitude, longitude):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'latlng': f'{latitude},{longitude}',
        'key': 'AIzaSyC9Uhy7ZXhqS6R0joT9Jcs88mhdJHNRk3c'
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Initialize variables
    output = {
        "street_number": "none",
        "postal_code": "none",
        "city": "none",
        "state": "none",
        "country": "none"
    }

    if data['status'] == 'OK':
        results = data['results']
        if results:
            address_components = results[0]['address_components']
            # Loop through address components and extract the desired parts
            for component in address_components:
                types = component['types']
                if 'establishment' in types:
                    output["street_number"] = component['long_name']
                elif 'postal_code' in types:
                    output["postal_code"] = component['long_name']
                elif 'locality' in types:
                    output["city"] = component['long_name']
                elif 'administrative_area_level_1' in types:
                    output["state"] = component['long_name']
                elif 'country' in types:
                    output["country"] = component['long_name']
    
    return output

def create_default_user(request=None):
    if (settings.DEBUG):
        user = User.objects.create_user(username='admin@gmail.com', email='admin@gmail.com', password='admin',is_superuser=True, first_name="admin", last_name="admin",is_staff=True)
        return HttpResponse()
    else:
        return HttpResponseNotFound()