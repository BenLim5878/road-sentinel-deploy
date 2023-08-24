import os
import mimetypes
import json
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse ,HttpResponseNotFound, HttpResponseRedirect
from django.conf import settings
from core.models import ImageAnnotation, GeoLocationGoogle, UserImage
from django.core.exceptions import ObjectDoesNotExist
from .models import SystemConfiguration
from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from collections import defaultdict
from django.db.models import Count, Sum
from datetime import timedelta, datetime
from django.db.models.functions import ExtractHour, TruncHour
from django_q.tasks import async_task
from django.contrib.auth import authenticate, login, logout

def serve_html(request, path=None):
    # Construct the absolute file path
    file_path = ""
    session_id = request.COOKIES.get('sessionid')
    if (session_id):
        try:
            session = request.session  # Access the session
            if session.get_expiry_date() < timezone.now():
                return redirect("login")
            else:
                if (path is None):
                    file_path = os.path.join(settings.VIEW_STATIC_ROOT, "html", "index.html")
                elif (path == "dashboard"):
                    file_path = os.path.join(settings.VIEW_STATIC_ROOT, "html", "dashboard.html")
                elif (path == "setting"):
                    file_path = os.path.join(settings.VIEW_STATIC_ROOT, "html", "setting.html")
                else:
                    return HttpResponseRedirect("/app/")
        except KeyError:
            return redirect("login")
    else:
        return redirect("login")
    # Read the file contents
    with open(file_path, 'r') as file:
        file_contents = file.read()

    # Return the file contents as an HTTP response
    return HttpResponse(file_contents, content_type='text/html')

def serve_img(request, img_name):
    # Construct the absolute file path
    image_path = os.path.join(settings.VIEW_STATIC_ROOT, 'img', img_name)
    
   # Check if the image file exists
    if os.path.exists(image_path):
        content_type, _ = mimetypes.guess_type(image_path)
        if content_type:
            with open(image_path, 'rb') as f:
                return HttpResponse(f.read(), content_type=content_type)
        else:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()
    
def serve_css(request, css_filename):
    # Construct the absolute file path
    css_path = os.path.join(settings.VIEW_STATIC_ROOT, 'css', css_filename)
    # Check if the CSS file exists
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            return HttpResponse(f.read(), content_type='text/css')
    else:
        return HttpResponseNotFound()
    
def serve_geo_data(request):
    out = []
    user_image = UserImage.objects.all()
    for data in user_image:
        geo_location_google = GeoLocationGoogle.objects.get(uuid=str(data.uuid))
        try:
            image_annotation = ImageAnnotation.objects.get(uuid_id=str(data.uuid))
            obj_data = {
                "id": data.uuid,
                "isAnnotated": True,
                "entryDate": {
                    "year": data.entryDate.year,
                    "month": data.entryDate.month,
                    "day": data.entryDate.day,
                    "hours": data.entryDate.hour,
                    "minutes": data.entryDate.minute,
                    "display": data.entryDate.strftime("%d %B %Y %I:%M%p")
                },
                "annotation":{
                    "processTimestamp": {
                    "year": image_annotation.processTimestamp.year,
                    "month": image_annotation.processTimestamp.month,
                    "day": image_annotation.processTimestamp.day,
                    "hours": image_annotation.processTimestamp.hour,
                    "minutes": image_annotation.processTimestamp.minute,
                    "display": image_annotation.processTimestamp.strftime("%d %B %Y %I:%M%p")
                },
                    "pothole": image_annotation.numPothole,
                    "isAcknowledged": image_annotation.isAcknowledged
                },
                "location":{
                    "latlng":{
                        "latitude": geo_location_google.latitude,
                        "longitude": geo_location_google.longitude
                    },
                    "address":{
                        "streetNumber": geo_location_google.streetNumber,
                        "postalCode": geo_location_google.postalCode,
                        "city": geo_location_google.city,
                        "state": geo_location_google.state,
                        "country": geo_location_google.country
                    }
                }
            }
            out.append(obj_data)
        except ObjectDoesNotExist:
            obj_data = {
                "id": data.uuid,
                "isAnnotated": False,
                "entryDate": {
                    "year": data.entryDate.year,
                    "month": data.entryDate.month,
                    "day": data.entryDate.day,
                    "hours": data.entryDate.hour,
                    "minutes": data.entryDate.minute,
                    "display": data.entryDate.strftime("%d %B %Y %I:%M%p")
                },
                "location":{
                    "latlng":{
                        "latitude": geo_location_google.latitude,
                        "longitude": geo_location_google.longitude
                    },
                    "address":{
                        "streetNumber": geo_location_google.streetNumber,
                        "postalCode": geo_location_google.postalCode,
                        "city": geo_location_google.city,
                        "state": geo_location_google.state,
                        "country": geo_location_google.country
                    }
                }
            }
            out.append(obj_data)
    
    json_out = json.dumps(out)
    return HttpResponse(json_out, content_type='application/json')

def serve_geo_data_country(request):
    out = {
        "east_malaysia_total_potholes": 0,
        "west_malaysia_total_potholes": 0
    }
    user_image = UserImage.objects.all()
    for data in user_image:
        geo_location_google = GeoLocationGoogle.objects.get(uuid=str(data.uuid))
        try:
            image_annotation = ImageAnnotation.objects.get(uuid_id=str(data.uuid))
            if image_annotation.numPothole > 0:
                if geo_location_google.state == "Sarawak" or geo_location_google.state == "Sabah" or geo_location_google.state == "Labuan Federal Territory":
                    out["east_malaysia_total_potholes"] += 1
                else:
                    out["west_malaysia_total_potholes"] += 1
        except ObjectDoesNotExist:
            continue
    
    json_out = json.dumps(out)
    return HttpResponse(json_out, content_type='application/json')

def serve_geo_data_state(request):
    out = {
        "Johor":0,
        "Kedah": 0,
        "Kelantan": 0,
        "Melaka": 0,
        "Negeri Sembilan": 0,
        "Pahang": 0,
        "Perak": 0,
        "Perlis": 0,
        "Pulau Pinang": 0,
        "Sabah": 0,
        "Sarawak": 0,
        "Selangor": 0,
        "Terengganu": 0,
        "Wilayah Persekutuan Kuala Lumpur": 0,
        "Labuan Federal Territory": 0,
        "Putrajaya": 0
    }
    user_image = UserImage.objects.all()
    for data in user_image:
        geo_location_google = GeoLocationGoogle.objects.get(uuid=str(data.uuid))
        try:
            image_annotation = ImageAnnotation.objects.get(uuid_id=str(data.uuid))
            if image_annotation.numPothole > 0:
                out[geo_location_google.state] += 1
        except ObjectDoesNotExist:
            continue
    
    json_out = json.dumps(out)
    return HttpResponse(json_out, content_type='application/json')

@csrf_exempt
def serve_annotation_data(request, annotation_id = ""):
    if  request.method == 'PUT':
        data = json.loads(request.body)
        try:
            instance = ImageAnnotation.objects.get(pk=data["id"])
            instance.isAcknowledged = data["isAcknowledged"]
            instance.save()
            return HttpResponse('Annotation has been updated successfully!')
        except ObjectDoesNotExist:
            return HttpResponse('Annotation is not found ...')
    elif request.method == 'GET':
        out = {}
        try:
            user_image = UserImage.objects.get(pk=annotation_id)
            image_annotation = ImageAnnotation.objects.get(pk=annotation_id)
            geo_location_google = GeoLocationGoogle.objects.get(pk=annotation_id)
            
            out = {
                    "id": user_image.uuid,
                    "isAnnotated": True,
                    "entryDate": {
                        "year": user_image.entryDate.year,
                        "month": user_image.entryDate.month,
                        "day": user_image.entryDate.day,
                        "hours": user_image.entryDate.hour,
                        "minutes": user_image.entryDate.minute,
                        "display": user_image.entryDate.strftime("%d %B %Y %I:%M%p")
                    },
                    "annotation":{
                        "processTimestamp": {
                        "year": image_annotation.processTimestamp.year,
                        "month": image_annotation.processTimestamp.month,
                        "day": image_annotation.processTimestamp.day,
                        "hours": image_annotation.processTimestamp.hour,
                        "minutes": image_annotation.processTimestamp.minute,
                        "display": image_annotation.processTimestamp.strftime("%d %B %Y %I:%M%p")
                    },
                        "pothole": image_annotation.numPothole,
                        "isAcknowledged": image_annotation.isAcknowledged
                    },
                    "location":{
                        "latlng":{
                            "latitude": geo_location_google.latitude,
                            "longitude": geo_location_google.longitude
                        },
                        "address":{
                            "streetNumber": geo_location_google.streetNumber,
                            "postalCode": geo_location_google.postalCode,
                            "city": geo_location_google.city,
                            "state": geo_location_google.state,
                            "country": geo_location_google.country
                        }
                    }
                }
            
        except ObjectDoesNotExist:
            out = {
                "response": "The requested image annotation does not exist ..."
            }
        return JsonResponse(out,content_type='application/json')
    

@csrf_exempt
def serve_system_configuration_setting(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        instance = SystemConfiguration.objects.get(pk=1)
        instance.NUM_IMAGE_THRESHOLD = data["NUM_IMAGE_THRESHOLD"]
        instance.MAP_INITIAL_ZOOM_LEVEL = data["MAP_INITIAL_ZOOM_LEVEL"]
        instance.MAP_MAXIMUM_ZOOM_LEVEL = data["MAP_MAXIMUM_ZOOM_LEVEL"]
        instance.MAP_MINIMUM_ZOOM_LEVEL = data["MAP_MINIMUM_ZOOM_LEVEL"]
        instance.save()

        return HttpResponse("Setting saved successfully!")
    
    if request.method == 'GET':
        setting =  SystemConfiguration.objects.first()
        out = model_to_dict(setting)
        out.pop('id',None)
        return JsonResponse(out)
    
def page_not_found(request,exception):
    file_path = os.path.join(settings.VIEW_STATIC_ROOT, "html", "404.html")
    # Read the file contents
    with open(file_path, 'r') as file:
        file_contents = file.read()

    # Return the file contents as an HTTP response
    return HttpResponse(file_contents, content_type='text/html')

def serve_statistic_data(request):
    out = {
        "total_annotations": {
            "number": 0,
            "since_last_month": 0
        },
        "total_potholes": {
            "number": 0,
            "since_last_month": 0
        },
        "prob_potholes_by_image": 0,
        "total_unacknowledged_annotations": 0,
        "total_acknowledged_annotations": 0,
        "percent_acknowledged_annotations": 0,
        "average_user_image_received_by_hour": {
            "number": 0,
            "unit": "hour",
            "based_on" : "0 days"
        },
        "average_image_process_by_hour": {
            "number": 0,
            "unit": "hour",
            "based_on" : "0 days"
        },
        "total_potholes_by state":{
            "Johor":0,
            "Kedah": 0,
            "Kelantan": 0,
            "Melaka": 0,
            "Negeri Sembilan": 0,
            "Pahang": 0,
            "Perak": 0,
            "Perlis": 0,
            "Pulau Pinang": 0,
            "Sabah": 0,
            "Sarawak": 0,
            "Selangor": 0,
            "Terengganu": 0,
            "Wilayah Persekutuan Kuala Lumpur": 0,
            "Labuan Federal Territory": 0,
            "Putrajaya": 0
        },
        "total_potholes_by_day_past_month":{
            "date":[],
            "pothole":[]
        }
    }
    
    # Data
    image_annotations = ImageAnnotation.objects.all()
    user_images = UserImage.objects.all()
    geo_locations = GeoLocationGoogle.objects.all()
    
    # Total number of annotated image and total potholes
    for annotation in image_annotations:
        if annotation.numPothole > 0:
            out["total_annotations"]["number"] += 1
            out["total_potholes"]["number"] += annotation.numPothole
    
    # Increase or decrease since last month
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    previous_month = (current_month - 1) if current_month != 1 else 12
    previous_year = current_year if current_month != 1 else (current_year - 1)
    current_month_data = ImageAnnotation.objects.filter(
        processTimestamp__year=current_year, 
        processTimestamp__month=current_month
    )
    previous_month_data = ImageAnnotation.objects.filter(
        processTimestamp__year=previous_year, 
        processTimestamp__month=previous_month
    )
    current_month_annotations = current_month_data.count()
    previous_month_annotations = previous_month_data.count()
    current_month_potholes =  0 if current_month_data.aggregate(Sum('numPothole'))['numPothole__sum'] == None else current_month_data.aggregate(Sum('numPothole'))['numPothole__sum']
    previous_month_potholes = 0 if previous_month_data.aggregate(Sum('numPothole'))['numPothole__sum'] == None else previous_month_data.aggregate(Sum('numPothole'))['numPothole__sum']
    if (previous_month_annotations > 0):
        out["total_annotations"]["since_last_month"] = ((current_month_annotations - previous_month_annotations) / previous_month_annotations) * 100 
        out["total_potholes"]["since_last_month"] = ((current_month_annotations - previous_month_annotations) / previous_month_annotations) * 100 
    else :
        out["total_annotations"]["since_last_month"] = 0
        out["total_potholes"]["since_last_month"] = 0
            
    # Probability of potholes per image
    if (len(user_images) > 0):
        out["prob_potholes_by_image"] = "{:.2f}".format((out["total_annotations"]["number"] / len(user_images)) * 100)
    else:
        out["prob_potholes_by_image"] = "{:.2f}".format(0)
        
    # Total unacknowledged annotations
    for annotation in image_annotations:
        if annotation.numPothole > 0:
            if annotation.isAcknowledged:
                out["total_acknowledged_annotations"] += 1
            else:
                out["total_unacknowledged_annotations"] += 1
                
    # Percent of acknowledged annotations
    if (out["total_annotations"]["number"]):
        out["percent_acknowledged_annotations"] =  "{:.2f}".format((out["total_acknowledged_annotations"] / out["total_annotations"]["number"]) * 100)
    else:
        out["percent_acknowledged_annotations"] = "{:.2f}".format(0)
        
    # Total potholes by state
    for annotation in image_annotations:
        location = GeoLocationGoogle.objects.get(pk=annotation.uuid)
        state = location.state
        out["total_potholes_by state"][state] +=  1
    
    # Total potholes by day past month
    total_days = 30
    current_date = datetime.now()
    one_month_ago = current_date - timedelta(days=30)
    pothole_data = ImageAnnotation.objects.filter(processTimestamp__gte=one_month_ago, processTimestamp__lte=current_date)
    total_potholes_by_day = defaultdict(int)

    for data in pothole_data:
        date = data.processTimestamp.date()
        total_potholes_by_day[date] += data.numPothole
    for i in range(total_days):
        date = (one_month_ago + timezone.timedelta(days=i)).date()
        out["total_potholes_by_day_past_month"]["date"].append(date.strftime("%Y-%m-%d"))
        out["total_potholes_by_day_past_month"]["pothole"].append(total_potholes_by_day[date])

    # Average user image received by hour
    total_days = 30
    now = timezone.now()
    ten_days_ago = now - timedelta(days=total_days)
    images = UserImage.objects.filter(entryDate__range=[ten_days_ago, now])
    images = images.annotate(hour=ExtractHour(TruncHour('entryDate'))).values('hour').annotate(count=Count('uuid'))
    out["average_user_image_received_by_hour"]["number"] =  "{:.4f}".format(sum(image['count'] for image in images) / (24 * total_days))
    out["average_user_image_received_by_hour"]["based_on"] =  f'{total_days} days'
    
    # Average image processed by hour
    total_days = 30
    now = timezone.now()
    ten_days_ago = now - timedelta(days=total_days)
    images = ImageAnnotation.objects.filter(processTimestamp__range=[ten_days_ago, now])
    images = images.annotate(hour=ExtractHour(TruncHour('processTimestamp'))).values('hour').annotate(count=Count('uuid'))
    out["average_image_process_by_hour"]["number"] =  "{:.4f}".format(sum(image['count'] for image in images) / (24 * total_days))
    out["average_image_process_by_hour"]["based_on"] =  f'{total_days} days'

    return JsonResponse(out)

@csrf_exempt
def serve_login_page(request):
    if request.method == 'GET':
        session_id = request.COOKIES.get('sessionid')
        if (session_id):
            session = request.session
            if session.get_expiry_date() > timezone.now():
                return HttpResponseRedirect("/app/")
        
        logout(request)
        file_path = os.path.join(settings.VIEW_STATIC_ROOT, "html", "login.html")
        # Read the file contents
        with open(file_path, 'r') as file:
            file_contents = file.read()
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(request, username=data["email"], password=data["password"])
        if user is not None:
            # Save session
            login(request, user)
            request.session.set_expiry(24 * 60 * 60)
            # Update user last login field
            user.last_login = timezone.now()
            user.save()
            return JsonResponse({"id": user.id,"status":True})
        else:
            logout(request)
            return JsonResponse({"status":False})
        

    # Return the file contents as an HTTP response
    return HttpResponse(file_contents, content_type='text/html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/app/login/')