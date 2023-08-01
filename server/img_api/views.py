from django.http import FileResponse
from django.http import HttpResponseNotFound
import os

def get_image(request,filename):
    
    # Define the path to the image file
    image_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image_output')
    image_path = None
    
    # Check if the image file exists
    if os.path.exists(image_folder_path):
        for folder_name in os.listdir(image_folder_path):
            folder_path = os.path.join(image_folder_path, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    if file_name == filename:
                        image_path = os.path.join(folder_path, file_name)
                        
        if image_path is not None:
            return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
        else:
            return HttpResponseNotFound('Image not found')
    else:
        # Return a 404 response if the image file doesn't exist
        return HttpResponseNotFound('Image not found')
