from odoo import http
from ..utils.api_utils import json_error
from ..utils.jwt_encode import JWTEncoder


def verify_access_token(func):
    def wrapper(*args, **kwargs):
        # ==================== VERIFY API KEY ====================

        # ==================== CALL CONTROLLER METHOD ====================

        result = func(*args, **kwargs)

        # You can perform additional post-processing here

        return result

    return wrapper
