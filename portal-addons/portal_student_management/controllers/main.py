from odoo import http
from werkzeug.wrappers.response import Response
from werkzeug.security import generate_password_hash, check_password_hash
import re

from ..utils.jwt_encode import JWTEncoder
from datetime import datetime, timedelta
from ..utils.api_utils import json_response, exclude_keys_from_dict, json_error, json_success, get_body_json


class StudentAPI(http.Controller):
    @http.route('/api/student/register', auth='public', method=['POST'], type='http', cors='*', csrf=False)
    def student_register(self, **kwargs):
        """
        API để đăng ký học viên
        1. Lấy dữ liệu từ request
        2. Kiểm tra dữ liệu hợp lệ
           a. Kiểm tra dữ liệu có đầy đủ không (missing input)
           b. Kiểm tra password và password_confirm 
        3. Kiểm tra email đã được đăng ký chưa
        4. Hash password
        5. Tạo học viên
        """
        # 1. Lấy dữ liệu từ request
        request_data = get_body_json(http.request)

        # 2. Kiểm tra dữ liệu hợp lệ
        name = request_data.get('name')
        email = request_data.get('email')
        password = request_data.get('password')
        password_confirm = request_data.get('password_confirm')

        # 2.a. Kiểm tra dữ liệu có đầy đủ không (missing input)
        if not name or not email or not password or not password_confirm:
            return json_error('Missing input data', 400)

        # 2.b. Kiểm tra password và password_confirm
        elif password != password_confirm:
            return json_error('Password and confirm password do not match', 400)

        # 3. Kiểm tra email đã được đăng ký chưa
        student = http.request.env['portal.student'].sudo().search(
            [('email', '=', email)])
        if student:
            return json_error('Email already registered', 400)

        # 4. Hash password
        password_hash = generate_password_hash(password)

        # 5. Tạo học viên
        created_student = http.request.env['portal.student'].sudo().create({
            'name': name,
            'email': email,
            'password_hash': password_hash,

        })

        response = json_success('Student created successfully', 201)

        return response
