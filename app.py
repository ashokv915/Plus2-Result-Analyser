from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import subprocess
import json
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FOLDER = "./logs"
LOG_FILE = "./logs/app.log"
os.makedirs(LOG_FOLDER,exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configuration
UPLOAD_FOLDER = './uploads'
RESULT_FOLDER = './results'
RESULT_FILE_NAME = "final.pdf"
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER,exist_ok=True)
logging.info("All required folders are created+++++++")
print("Created folders...........")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed PDF result"""
    try:
        file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if the post request has the file part
        if 'pdfFile' not in request.files:
            logging.error('error:No PDf file provided ',exc_info=True)
            return jsonify({'error': 'No PDF file provided'}), 400
        
        file = request.files['pdfFile']

        # Check if file is selected
        if file.filename == '':
            logging.error('error:No file selected', exc_info=True)
            return jsonify({'error': 'No file selected'}), 400
        
        # Get text values
        topn = request.form.get('topn','10')
        #text2 = request.form.get('text2', '')
        firstreg = request.form.get('firstreg', 24000000)
        #text4 = request.form.get('text4', '')

        logging.debug('values are {0} {1}'.format(topn,firstreg))
        print("Values are "+topn+" "+firstreg)
        # Validate text inputs
        if not all([topn,firstreg]):
            logging.error('Values are missing.',exc_info=True)
            return jsonify({'error': 'All text fields are required'}), 400
        
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Create unique filename to avoid conflicts
            import time
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            logging.info("File name is "+filename)
            
            # Save the uploaded file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logging.info("Uploaded file path is "+filepath)
            print("++++++++++++++++++++++++++++")
            
            # Prepare data for Python script
            script_data = {
                'pdf_path': filepath,
                'topn': topn,
                'firstreg': firstreg,
                'filename': filename,
                'result_folder': app.config['RESULT_FOLDER']
            }
            logging.debug("data to python script is "+','.join(str(value) for value in script_data.values()))

            # Run the Python processing script
            result_info = run_processing_script(script_data)
            
            if result_info['success']:
                # Clean up uploaded file after processing (optional)
                # os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'message': 'PDF processed successfully!',
                    'result_file': result_info['result_filename'],
                    'processing_details': result_info['details']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result_info['error']
                }), 500
        
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def run_processing_script(data):
    """
    Run your custom Python script with the uploaded PDF and text values
    Returns info about the generated result PDF file
    """
    logging.info("inside the run processing script function")
    try:
        # Create temporary JSON file with parameters
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data, temp_file)
            temp_json_path = temp_file.name
        
        try:
            # Run the processing script
            print("Running the script+++++++++")
            script_path = 'main.py'
            result = subprocess.run([
                'python3', script_path, data['pdf_path'], data['topn'],data['firstreg'],RESULT_FOLDER,RESULT_FILE_NAME
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            logging.debug("File for upload : "+data['pdf_path'])
            logging.info("Output of the script is "+result.stdout)
            logging.error("Error "+result.stderr)

            if result.returncode == 0:
                # Script executed successfully
                output_lines = result.stdout.strip().split('\n')
                logging.debug("Output lines"+','.join(output_lines))
                
                # Look for the result PDF filename in the output
                result_filename = None
                for line in output_lines:
                    if line.startswith('Results saved to:'):
                        result_filename = line.replace('Results saved to:', '').strip()
                        print(result_filename)
                        logging.debug("File name (inside script) : "+result_filename)
                        break
                
                if result_filename and os.path.exists(os.path.join(data['result_folder'], result_filename)):
                    return {
                        'success': True,
                        'result_filename': result_filename,
                        'details': result.stdout.strip()
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Result PDF file was not generated properly'
                    }
            else:
                # Script failed
                error_msg = result.stderr.strip()
                logging.error(error_msg,stack_info=True)
                return {
                    'success': False,
                    'error': f"Processing failed: {error_msg}"
                }
                
        finally:
            # Clean up temporary file
            os.unlink(temp_json_path)
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Processing timeout - script took too long to execute"
        }
    except Exception as e:
        logging.error(e)
        print("Error........."+e.stderr)
        return {
            'success': False,
            'error': f"Processing error: {str(e)}"
        }

if __name__ == '__main__':
    try:
        print("Starting PDF Processing Server...")
        print("Upload folder:", os.path.abspath(UPLOAD_FOLDER))
        print("Result folder:", os.path.abspath(RESULT_FOLDER))
        print("Server running at: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(e)
        print("Error ......."+e.stderr)