import re
import json
from odoo.http import request
from ..utils.utils import json_response


def check_url(url_field):
    """
    Decorator validate url_field trong body của POST request có đúng định dạng URL không.
    Return Http Response 400 nếu invalid.
    """

    def decorator(origin_function):
        def wrapper(*args, **kwargs):
            request_data = json.loads(request.httprequest.data)

            if url_field not in list(request_data.keys()):
                return json_response(400, _missing_field_template(url_field))

            url = request_data.get(url_field)
            if not isinstance(url, str):
                return json_response(
                    400, _invalid_field_template(url_field, url)
                )

            regex = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

            localhost_regex = "^http:\\/\\/localhost.*$"

            if not re.match(regex, url, re.IGNORECASE) and not re.match(
                localhost_regex, url, re.IGNORECASE
            ):
                return json_response(
                    400, _invalid_field_template(url_field, url)
                )

            return origin_function(*args, **kwargs)

        return wrapper

    return decorator


def check_fields_presence(*required_fields):
    """
    Decorator validate có thiếu field nào trong body POST request không.
    Return Http Response 400 nếu invalid.
    """

    def decorator(origin_function):
        def wrapper(*args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            request_fields = list(request_data.keys())

            for field in required_fields:
                if field not in request_fields:
                    return json_response(400, f"Missing field: '{field}")

            return origin_function(*args, **kwargs)

        return wrapper

    return decorator


def _missing_field_template(field):
    return f"Missing field: '{field}'"


def _invalid_field_template(field_name, field_value, requirement=""):
    message = f"Invalid field: '{field_name}': '{field_value}'."

    if requirement != "":
        message += f" Required: {requirement}."

    return message
