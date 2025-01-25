from flask import Flask, request, render_template, send_file
import pytesseract
from PIL import Image
from io import BytesIO
import base64
import os
import uuid

app = Flask(__name__)

# Folder to store uploaded and processed images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OCR text storage
extracted_text = ""  # Store the extracted text for later download

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle multiple file uploads and perform OCR."""
    global extracted_text
    extracted_text = ""  # Reset the extracted text

    # Handle multiple uploaded images
    if 'file' in request.files:
        files = request.files.getlist('file')  # Get the list of uploaded files
        if not files or files[0].filename == '':
            return "No valid files uploaded", 400

        # Process each uploaded file
        for file in files:
            try:
                unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)

                # Perform OCR on each uploaded image
                language = request.form.get('language', 'eng')  # Default to English
                text = pytesseract.image_to_string(Image.open(filepath), lang=language)
                extracted_text += f"--- Text from {file.filename} ---\n{text}\n\n"
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                extracted_text += f"--- Error processing {file.filename} ---\n\n"

    # Handle cropped image
    cropped_image_data = request.form.get('croppedImage')
    if cropped_image_data:
        try:
            # Decode and save the cropped image
            header, base64_data = cropped_image_data.split(',', 1)
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            unique_filename = f"cropped_{uuid.uuid4().hex}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(filepath)

            # Perform OCR on the cropped image
            language = request.form.get('language', 'eng')  # Default to English
            text = pytesseract.image_to_string(image, lang=language)
            extracted_text += f"--- Text from Cropped Image ---\n{text}\n\n"

        except Exception as e:
            print(f"Error processing cropped image: {e}")
            return "Error processing cropped image. Ensure the file is valid.", 500

    # Render the result page with the combined extracted text
    return render_template('index.html', text=extracted_text)

@app.route('/download')
def download_text():
    """Allow the user to download the extracted text."""
    global extracted_text

    # Check if extracted text exists
    if not extracted_text.strip():
        return "No text extracted to download.", 400

    # Save the extracted text to a file
    text_file_path = os.path.join(app.config['UPLOAD_FOLDER'], "extracted_text.txt")
    with open(text_file_path, "w") as f:
        f.write(extracted_text)

    # Serve the file for download
    return send_file(text_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)