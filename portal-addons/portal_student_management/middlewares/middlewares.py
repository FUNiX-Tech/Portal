from odoo import http
from ..utils.api_utils import json_error
import requests


def verify_access_token(func):
    def wrapper(*args, **kwargs):
        # ==================== VERIFY API KEY ====================
        # 1. Extract access token from cookie

        # Access Odoo environment
        env = http.request.env

        # Access the service_key_configuration model
        service_key_config = env["service_key_configuration"].sudo()

        access_token = http.request.httprequest.cookies.get("accessToken")

        # 2. Check access token exists
        if not access_token:
            return json_error("Access token not found", status=400)

        # 3. Construct API request
        # Retrieve the base URL
        base_url = service_key_config.get_api_key_by_service_name("LMS_BASE")
        endpoint = "api/user/v1/user-info"

        url = f"{base_url}{endpoint}"

        # 4. Send API request
        data = {"token": access_token}
        response = requests.post(url, data=data)

        if response.status_code > 300:
            return json_error("Something went wrong", status=500)

        kwargs["user_info"] = response.json()

        # ==================== CALL CONTROLLER METHOD ====================

        result = func(*args, **kwargs)

        # You can perform additional post-processing here

        return result

    return wrapper
