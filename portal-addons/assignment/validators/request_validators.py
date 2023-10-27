import re
import json
from odoo.http import request
from ..utils.utils import json_response

def check_url(url_field):
    def wrapper_outer(origin_function):
        def wrapper_inner(*args, **kwargs):

            request_data = json.loads(request.httprequest.data)

            if url_field not in list(request_data.keys()):
                return json_response(400, _missing_field_template(url_field))

            url = request_data.get(url_field)
            print(type(url))
            if type(url) != str:
                return json_response(400, _invalid_field_template(url_field, url))
            
            regex = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

            if not re.match(regex, url, re.IGNORECASE):
                return json_response(400, _invalid_field_template(url_field, url))

            return origin_function(*args, **kwargs)

        return wrapper_inner
    return wrapper_outer

def check_fields_presence(*required_fields):
    def wrapper_outer(origin_function):
        def wrapper_inner(*args, **kwargs):

            request_data =json.loads(request.httprequest.data)

            request_fields = list(request_data.keys())

            for field in required_fields:
                if field not in request_fields: 
                    return json_response(400, f"Missing field: '{field}")

            return origin_function(*args, **kwargs)
        return wrapper_inner
    return wrapper_outer

def _missing_field_template(field):
    return f"Missing field: '{field}'"

def _invalid_field_template(field_name, field_value, requirement=""):
    message =  f"Invalid field: '{field_name}': '{field_value}'."

    if requirement != "":
        message += f" Required: {requirement}."

    return message