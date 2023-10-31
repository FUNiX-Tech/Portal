from odoo import http
import json
from werkzeug.wrappers.response import Response
from ..utils.api_utils import get_body_json, json_response, json_success, json_error
from ..utils.jwt_encode import JWTEncoder


def verify_access_token(func):
    def wrapper(*args, **kwargs):

        # ==================== VERIFY ACCESS TOKEN ====================

        # 1. Lâý access token từ cookie
        access_token = http.request.httprequest.cookies.get('access_token')

        # 2. Kiểm tra access token có tồn tại không
        if not access_token:
            return json_error('Access token not found', status=400)

        # 3. Decode access token
        decoded_access_token = JWTEncoder.decode_jwt(access_token)

        # 4. Kiểm tra thông tin access token có đầy đủ không
        if 'email' not in decoded_access_token or 'student_id' not in decoded_access_token or 'student_name' not in decoded_access_token:
            return json_error('Access token invalid', status=400)

        # 5. Lấy thông tin từ access token
        kwargs['decoded_access_token'] = decoded_access_token

        # ==================== CALL CONTROLLER METHOD ====================

        result = func(*args, **kwargs)

        # You can perform additional post-processing here

        return result
    return wrapper
