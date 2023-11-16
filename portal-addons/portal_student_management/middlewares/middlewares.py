from odoo import http
from ..utils.api_utils import json_error
import requests


def verify_access_token(func):
    def wrapper(*args, **kwargs):
        # ==================== VERIFY API KEY ====================
        # 1. Extract access token from cookie
        access_token = http.request.httprequest.cookies.get("accessToken")

        print("accessToken", access_token)
        # 2. Check access token exists
        if not access_token:
            return json_error("Access token not found", status=400)

        # 3. Construct API request
        url = "https://test-xseries.funix.edu.vn/api/user/v1/user-info"

        # 4. Send API request
        data = {"token": access_token}
        response = requests.post(url, data=data)

        if response.status_code > 300:
            return json_error("Something went wrong", status=500)

        # ==================== CALL CONTROLLER METHOD ====================

        result = func(*args, **kwargs)

        # You can perform additional post-processing here

        return result

    return wrapper
