import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import numpy as np
import os
import glob
from models.model import run_yolo
from .models import UserImage, ImageAnnotation,GeoLocationGoogle
import datetime
import requests
from sentinel_view.models import SystemConfiguration
from django_q.tasks import async_task
from django.utils import timezone
from django.conf import settings

def check_upload_validity(request):
    if (settings.DEBUG):
        return True
    
    current_time = timezone.localtime(timezone.now())    
    current_hour = current_time.hour
    if 8 <= current_hour < 18:
        return True
    else:
        return False

def upload_validity(request):
    isValid = check_upload_validity(request)
    if (isValid):
        return JsonResponse({'isValid':True, 'message': 'Session is established.'})
    else:
         return JsonResponse({'isValid':False, 'message': 'Please run the application on the specified time (8am - 6pm), or session has expired.'})
        

@csrf_exempt
def process_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        
        if (not check_upload_validity(request)):
            return JsonResponse({'message':'Please run the application on the specified time (8am - 6pm), or session has expired.'})
        
        # GPS coordinate checking
        if request.POST.get('latitude', None) is not None and request.POST.get('longitude', None) is not None:
            # Retrive GPS coordinates
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
        else:
            return JsonResponse({'message': 'Image processed but missing GPS coordinates.'})
        
        # Retrieve the uploaded image
        image_file = request.FILES['image']
        
        
        # Process the image
        image = Image.open(image_file)
        image = image.convert('RGB')
        
        # Run image pipline
        async_task(save_incoming_image, image, latitude, longitude)
        
        return JsonResponse({'message': 'Image processed and saved successfully.'})
    else:
        return JsonResponse({'message': 'Invalid request.'})
    
def save_incoming_image(image, latitude, longitude):
    # Define the destination path
    destination_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp_img')

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Generate a unique filename
    image_uuid = str(uuid.uuid4())
    filename = image_uuid + '.jpg'
    
    # Get current date time
    current_datetime = datetime.datetime.now()
    
    # Save the image to the destination path
    image.save(os.path.join(destination_path, filename),'JPEG')
    
    # Create a UserImage instance
    user_image = UserImage(uuid=image_uuid, entryDate=current_datetime)
    
    user_image.save()
    
    process_latlong(user_image, latitude, longitude)
    check_original_image_folder(destination_path)
    
def check_original_image_folder(destination_path):
     # Check the number of images in the folder
    image_count = len(glob.glob(os.path.join(destination_path, '*.jpg')))
    if (image_count >= SystemConfiguration.objects.first().NUM_IMAGE_THRESHOLD):
        annotations = run_yolo()
        delete_original_content(destination_path)
        if (annotations):
            if len(annotations) > 0:
                process_timestamp_str = annotations['folder_name']
                process_timestamp_obj = datetime.datetime.strptime(process_timestamp_str, "%Y-%m-%d_%H.%M.%S.%f")
                for annotation in annotations['annotations']:
                    img_uid = annotation['img_uid']
                    num_pothole = annotation['num_pothole']
                    user_image = UserImage.objects.get(uuid=img_uid)
                    image_annotation = ImageAnnotation(
                        uuid = user_image,
                        processTimestamp = process_timestamp_obj,
                        numPothole = num_pothole
                    )
                    image_annotation.save()
        
def delete_original_content(destination_path):
    file_list = os.listdir(destination_path)
    for file_name in file_list:
        file_path = os.path.join(destination_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            
def process_latlong(user_image, latitude, longitude):
    address_components = get_address(latitude, longitude)
    geo_location_google = GeoLocationGoogle(
        uuid = user_image,
        streetNumber = address_components["street_number"],
        postalCode = address_components["postal_code"],
        city = address_components["city"],
        state = address_components["state"],
        country = address_components["country"],
        latitude = latitude,
        longitude = longitude
    )
    geo_location_google.save()
    
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
