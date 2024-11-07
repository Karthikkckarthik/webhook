from os import environ
from flask import Flask, request, jsonify
# from flask_cors import CORS


import json
import logging
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)  # Changed from app to application for AWS compatibility

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'webhook_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_webhook_data(data, request_type):
    """Save webhook data to a file with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'webhook_data_{timestamp}.json'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(filepath, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'request_type': request_type,
            'headers': dict(request.headers),
            'data': data
        }, f, indent=4)
    
    return filename

@app.route('/')
def home():
    """Home route to confirm server is running"""
    return """
    <h1>Webhook Server is Running</h1>
    <p>Send POST requests to /webhook endpoint</p>
    """

@app.route('/webhook', methods=['POST', 'PUT', 'GET'])
def webhook():
    try:
        request_data = {}
        files_saved = []

        # Log the incoming request
        logger.info(f"Received {request.method} request from {request.remote_addr}")

        # Handle different content types
        content_type = request.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            request_data['json'] = request.get_json(silent=True) or {}
        elif 'application/x-www-form-urlencoded' in content_type:
            request_data['form'] = request.form.to_dict()
        elif 'multipart/form-data' in content_type:
            request_data['form'] = request.form.to_dict()
            if request.files:
                request_data['files'] = {}
                for filename, file in request.files.items():
                    if file.filename:
                        secure_name = secure_filename(file.filename)
                        save_path = os.path.join(UPLOAD_FOLDER, secure_name)
                        file.save(save_path)
                        files_saved.append(secure_name)
                        request_data['files'][filename] = secure_name
        else:
            request_data['raw'] = request.get_data(as_text=True)

        if request.args:
            request_data['query_params'] = dict(request.args)

        saved_filename = save_webhook_data(request_data, request.method)

        response = {
            'status': 'success',
            'message': 'Webhook data received successfully',
            'request_method': request.method,
            'content_type': content_type,
            'data_received': request_data,
            'files_saved': files_saved,
            'saved_filename': saved_filename
        }
        
        print(request_data)
        return jsonify(response), 200

    except Exception as e:
        error_msg = f"Error processing webhook: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500

if __name__ == '__main__':
    port = int(environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)

    