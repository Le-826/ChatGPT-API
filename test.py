import requests

# URL of the Flask server endpoint
url = 'http://127.0.0.1:8000/analyze_image'

# Path to the image file you want to send
image_path = 'data/1.png'

# Sending the image file to the server

with open(image_path, 'rb') as image_file:
    files = {'image': image_file}
    response = requests.post(url, files=files)
    
    # Check if the request was successful
    response.raise_for_status()

    # Print the response from the server
    print(response.json())
