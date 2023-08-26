import subprocess
import os
from datetime import datetime

def get_current_date_time():
    # Get the current date and time
    current_time = datetime.now()
    milliseconds = current_time.microsecond // 1000  # Convert microseconds to milliseconds
    return datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + f".{milliseconds:03d}"
    
def run_yolo():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'yolov7', 'detect.py')
    weight_path = os.path.join(script_dir, 'yolov7', 'best.pt')
    output_folder = f"{script_dir}/../image_output"
    folder_name = get_current_date_time()
    # command = f"py {script_path} --weights {weight_path} --conf 0.25 --img-size 640 --source {script_dir}/../tmp_img/ --project {output_folder} --name {folder_name} --save-txt"
    command = f"python3.9 {script_path} --weights {weight_path} --conf 0.25 --img-size 640 --source {script_dir}/../tmp_img/ --project {output_folder} --name {folder_name} --save-txt"
    subprocess.run(command, shell=True)
    annotations = yolo_post_processing(output_folder,folder_name)
    return annotations
    
def yolo_post_processing(output_folder, folder_name):
    image_folder = f"{output_folder}/{folder_name}"
    run_detect_dict = {
        "folder_name": folder_name,
        "annotations":[]
    }
    for file_name in os.listdir(image_folder):
        if file_name.endswith('.jpg'):
            file_name_without_extension = os.path.splitext(file_name)[0]
            labels_path = f"{output_folder}/{folder_name}/labels/{file_name_without_extension}.txt"
            
            annotations_dict = {
                    "img_uid": file_name_without_extension
            }
            
            if os.path.exists(labels_path):
                with open(labels_path, 'r') as file:
                    file_content = file.read()
                    file_content_list = file_content.split('\n')    
                    annotations_dict["num_pothole"] = len(file_content_list) - 1
            else:
                annotations_dict["num_pothole"] = 0
                
            run_detect_dict["annotations"].append(annotations_dict)
    
    return run_detect_dict
             
    
    
