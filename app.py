from flask import Flask, request, jsonify, render_template
import pytesseract
import re
from PIL import Image
import io

# Initialize the Flask app
app = Flask(__name__)

# Path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_blood_report_values(image):
    # Perform OCR on the raw image using Tesseract
    ocr_text = pytesseract.image_to_string(image)

    # Initialize a dictionary to store the extracted values
    values = {}

    # Define keywords for each parameter
    keywords = {
        'Total Cholesterol': ['Total Cholesterol', 'Cholesterol Total'],
        'HDL-Cholesterol': ['HDL-Cholesterol', 'HDL Cholesterol'],
        'LDL-Cholesterol': ['LDL-Cholesterol', 'LDL Cholesterol'],
        'Fasting Blood Sugar (FBS)': ['Fasting Blood Sugar', 'FBS', 'Glucose'],
        'Sodium': ['Sodium']
    }

    # Function to find the value near the keyword
    def find_value_near_keyword(text, keyword_list):
        for keyword in keyword_list:
            pattern = rf'{keyword}.*?(\d+\.\d+|\d+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    # Extract the values using the defined keywords
    for key, keyword_list in keywords.items():
        value = find_value_near_keyword(ocr_text, keyword_list)
        if value:
            values[key] = value

    # Initialize a list to store the output messages
    output = []

    # Check the extracted values and append messages to the output
    if 'Fasting Blood Sugar (FBS)' in values:
        glucose = float(values['Fasting Blood Sugar (FBS)'])
        if glucose > 5.6:
            output.append('Glucose level is high. Chances of diabetic.')
        elif glucose < 3.3:
            output.append('Glucose level is low.')
        else:
            output.append('Glucose level is normal.')

    if 'Sodium' in values:
        sodium = float(values['Sodium'])
        if sodium > 155:
            output.append('Sodium level is high.')
        elif sodium < 135:
            output.append('Sodium level is low.')
        else:
            output.append('Sodium level is normal.')

    if 'Total Cholesterol' in values:
        cholesterol = float(values['Total Cholesterol'])
        if cholesterol > 5.2:
            output.append('Total Cholesterol level is high.')
        else:
            output.append('Total Cholesterol level is normal.')

    return output

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        image = Image.open(io.BytesIO(file.read()))
        results = extract_blood_report_values(image)
        return jsonify({'results': results}), 200

if __name__ == '__main__':
    app.run(debug=True)
