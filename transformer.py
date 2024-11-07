import json

class WebhookMessage:
    def __init__(self, to, from_, text, receive_date, expiry_date, content_type,
                 media_type, message_id, end_user_name, button_reply_title=None,
                 button_reply_id=None, button_payload=None, latitude=None,
                 longitude=None):
        self.to = to
        self.from_ = from_  # 'from' is a reserved keyword in Python, so we use 'from_'
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
    """
    Transforms the incoming JSON response body to an instance of WebhookMessage.
    
    Args:
    - response_body (str or dict): The incoming JSON response from the webhook.
    
    Returns:
    - WebhookMessage: An instance of WebhookMessage populated with data from the JSON response.
    """
    # If the response body is a JSON string, parse it to a dictionary
    if isinstance(response_body, str):
        response_body = json.loads(response_body)
    
    # Extract the 'form' data from 'data_received' in the response body
    form_data = response_body.get("data_received", {}).get("form", {})
    
    # Map the extracted data to the WebhookMessage class
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

# Test example
if __name__ == "__main__":
    # Sample JSON response from webhook
    incoming_json = """
    {
      "status": "success",
      "message": "Webhook data received successfully",
      "request_method": "POST",
      "content_type": "application/x-www-form-urlencoded",
      "data_received": {
        "form": {
          "to": "917065017600",
          "from": "917483396805",
          "text": "hello kruthi",
          "ReceiveDate": "2024-11-07 16:48:16",
          "ExpiryDate": "2024-11-08 16:48:16",
          "content_type": "application/x-www-form-urlencoded",
          "media_type": "text",
          "Message_ID": "wamid.HBgMOTE3NDgzMzk2ODA1FQIAEhgUM0ZEMjUxREQ2NjkwQUJFRDQ3MDAA",
          "EndUserName": "Karthik K C"
        }
      }
    }
    """

    # Transform the incoming JSON to an instance of WebhookMessage
    webhook_message = transform_response_to_object(incoming_json)

    # Print the result to verify
    print(webhook_message)
