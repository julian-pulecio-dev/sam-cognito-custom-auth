import os
import json
import urllib.request
import urllib.parse

def send_cfn_response(event, context, response_status):
    """Send a response back to CloudFormation"""
    response_url = event.get("ResponseURL")
    if not response_url:
        return  # Not a CloudFormation event, do nothing
    
    response_body = {
        "Status": response_status,
        "Reason": f"See the details in CloudWatch Log Stream: {context.log_stream_name}",
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
    }
    
    json_response_body = json.dumps(response_body).encode()
    req = urllib.request.Request(response_url, data=json_response_body, method="PUT")
    req.add_header("Content-Type", "")
    req.add_header("Content-Length", str(len(json_response_body)))
    
    try:
        with urllib.request.urlopen(req) as response:
            print("CloudFormation response status:", response.status)
    except Exception as e:
        print("Error sending CloudFormation response:", str(e))

def verify_captcha(token):
    """Verify CAPTCHA token using Google reCAPTCHA API"""
    secret_key = os.environ['CAPTCHA_SECRET_KEY']
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = urllib.parse.urlencode({'secret': secret_key, 'response': token}).encode()
    
    req = urllib.request.Request(url, data=data, method="POST")
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        
    return result.get("success", False)

def handler(event, context):
    """Cognito Pre Sign-Up trigger with CloudFormation support"""
    print("Received event:", json.dumps(event))
    
    try:
        # Check if this is a CloudFormation event
        if "ResponseURL" in event:
            send_cfn_response(event, context, "SUCCESS")
            return
        
        # Handle normal Cognito Pre Sign-Up event
        client_metadata = event['request'].get('clientMetadata', {})
        captcha_token = client_metadata.get('captchaToken')

        if not captcha_token:
            raise Exception("Missing CAPTCHA token")

        if not verify_captcha(captcha_token):
            raise Exception("CAPTCHA validation failed")

        # Allow the sign-up process to continue
        return event

    except Exception as e:
        print("Error:", str(e))
        
        # If this was a CloudFormation request, report failure
        if "ResponseURL" in event:
            send_cfn_response(event, context, "FAILED")
        
        raise  # Re-raise the exception for normal Lambda errors
