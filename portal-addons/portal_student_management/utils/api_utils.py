from werkzeug.wrappers.response import Response
import json


def exclude_keys_from_dict(dictionary, *keys):
    """
    Function to exclude keys from dictionary

    @params:
    1. dictionary: dict
    2. keys: str containing keys to be excluded

    @return: dict without the excluded keys
    """
    return {key: value for key, value in dictionary.items() if key not in keys}


def json_response(data, status=200):
    """
    Function to return json response
    """
    return Response(
        json.dumps(data),
        status=status,
    )


def json_success(message, status=200):
    """
    Function to return json success response
    """
    return json_response(
        {"response": message, "status": status}, status=status
    )


def json_error(message, status=400):
    """
    Function to return json error response
    """
    return json_response({"error": message, "status": status}, status=status)


def get_body_json(request):
    """
    Function to get json from request body
    """

    data_body_str = request.httprequest.data.decode("utf-8")
    data_body_json = json.loads(data_body_str)
    return data_body_json
