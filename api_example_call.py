import requests

# Define the API endpoint
url = "http://127.0.0.1:5000/upload"  # Change this if the Flask app is running on a different host/port

# # Specify the file path to upload
# file_path = "test_data\OMCL2016.pdf"  # Replace with the actual PDF file path
# file_path = "test_data/s41598-022-07710-6.pdf"  
# file_path = "test_data/c27.pdf"  
# file_path = "test_data/b5 - not all fields.pdf"  
file_path = "test_data/error-2.pdf"  

# Open the file in binary mode and send the request
with open(file_path, 'rb') as file:
    files = {'file': (file_path, file, 'application/pdf')}
    response = requests.post(url, files=files)

# Print the response from the server
# print(response.json())
