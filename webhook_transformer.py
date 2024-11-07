from os import environ
from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the uploads folder for saving webhook data
UPLOAD_FOLDER = 'webhook_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class WebhookMessage:
    def __init__(self, to, from_, text, receive_date, expiry_date, content_type,
                 media_type, message_id, end_user_name, button_reply_title=None,
                 button_reply_id=None, button_payload=None, latitude=None,
                 longitude=None):
        self.to = to
        self.from_ = from_
        self.text = text
        self.receive_date = receive_date
        self.expiry_date = expiry_date
        self.content_type = content_type
        self.media_type = media_type
        self.message_id = message_id
        self.end_user_name = end_user_name
        self.button_reply_title = button_reply_title
        self.button_reply_id = button_reply_id
        self.button_payload = button_payload
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return (f"WebhookMessage(to={self.to}, from_={self.from_}, text={self.text}, "
                f"receive_date={self.receive_date}, expiry_date={self.expiry_date}, "
                f"content_type={self.content_type}, media_type={self.media_type}, "
                f"message_id={self.message_id}, end_user_name={self.end_user_name}, "
                f"button_reply_title={self.button_reply_title}, button_reply_id={self.button_reply_id}, "
                f"button_payload={self.button_payload}, latitude={self.latitude}, longitude={self.longitude})")

def transform_response_to_object(response_body):
    if isinstance(response_body, str):
        response_body = json.loads(response_body)
    
    form_data = response_body.get("data_received", {}).get("form", {})
    
    return WebhookMessage(
        to=form_data.get("to"),
        from_=form_data.get("from"),
        text=form_data.get("text"),
        receive_date=form_data.get("ReceiveDate"),
        expiry_date=form_data.get("ExpiryDate"),
        content_type=form_data.get("content_type"),
        media_type=form_data.get("media_type"),
        message_id=form_data.get("Message_ID"),
        end_user_name=form_data.get("EndUserName"),
        button_reply_title=form_data.get("BUTTON_REPLY_TITLE"),
        button_reply_id=form_data.get("BUTTON_REPLY_ID"),
        button_payload=form_data.get("ButtonPayload"),
        latitude=form_data.get("latitude"),
        longitude=form_data.get("longitude")
    )

def save_webhook_data(data, request_type):
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
    return """
    <h1>Webhook Server is Running</h1>
    <p>Send POST requests to /webhook endpoint</p>
    """

@app.route('/webhook', methods=['POST', 'PUT', 'GET'])
def webhook():
    try:
        request_data = {}
        files_saved = []

        logger.info(f"Received {request.method} request from {request.remote_addr}")

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

        webhook_message = transform_response_to_object({
            "data_received": request_data
        })

        response = {
            'status': 'success',
            'message': 'Webhook data received successfully',
            'request_method': request.method,
            'content_type': content_type,
            'data_received': request_data,
            'files_saved': files_saved,
            'saved_filename': saved_filename,
            'webhook_message': repr(webhook_message)
        }

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
