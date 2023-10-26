from odoo import http
from werkzeug.wrappers.response import Response
import json


def exclude_keys_from_dict(dictionary, *keys):
    """
    Hàm để loại bỏ các key trong dictionary

    @params:
    1. dictionary: dict
    2. keys: str chứa các key cần loại bỏ

    @return: dict mới không chứa các key trong args
    """
    return {key: value for key, value in dictionary.items() if key not in keys}


def json_response(data, status=200):
    """
    Hàm để trả về response dạng json

    """
    return Response(
        json.dumps(data),
        status=status,
    )


def json_success(message, status=200):
    """
    Hàm để trả về response dạng json success
    """
    return json_response({"response": message, "status": status}, status=status)


def json_error(message, status=400):
    """
    Hàm để trả về response dạng json error
    """
    return json_response({"error": message, "status": status}, status=status)


def get_body_json(request):
    """
    Hàm để lấy body của request dạng json
    """

    data_body_str = request.httprequest.data.decode('utf-8')
    data_body_json = json.loads(data_body_str)
    return data_body_json
