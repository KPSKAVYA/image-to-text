import os

# Path where we will save the file
upload_folder = 'static/uploads'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

# Try saving a test file
try:
    with open(os.path.join(upload_folder, 'test_file.txt'), 'w') as f:
        f.write("This is a test file.")
    print("Test file saved successfully.")
except Exception as e:
    print(f"Error saving file: {e}")
