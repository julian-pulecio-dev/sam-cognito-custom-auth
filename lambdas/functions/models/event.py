import base64
import json
import urllib
from dataclasses import dataclass, field, InitVar


@dataclass(frozen=True)
class Event:
  form_data:dict = field(init= False)
  lambda_event: InitVar[dict] = None

  def __post_init__(self, lambda_event:dict):
    headers = lambda_event.get("headers", {})
    content_type = headers.get("Content-Type", headers.get("content-type", ""))
    body = lambda_event.get("body", "")
    print('body:', body)
    print('content-type:', content_type)


    if lambda_event.get("isBase64Encoded", False):
      body = base64.b64decode(body).decode("utf-8")

    if "application/json" in content_type:
      form_data = json.loads(body)
          
    elif "application/x-www-form-urlencoded" in content_type:
      form_data = urllib.parse.parse_qs(body)
      form_data = {key: value[0] for key, value in form_data.items()}

    super().__setattr__('form_data', form_data) 