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

    @http.route('/api/student/login', auth='public', methods=['POST'], type='http', cors='*', csrf=False)
    def student_login(self, **kwargs):
        """
        API để đăng nhập học viên

        1. Lấy dữ liệu từ request
        2. Kiểm tra dữ liệu co đầy đủ không (missing input)
        3. Tìm học viên trong database
        4. Kiểm tra password có đúng không
        5. Tạo access token và refresh token
        6. Lưu refresh token vào database
        7. Trả về response với access token và refresh token trong cookies
        """

        # 1. Lấy dữ liệu từ request
        request_data = get_body_json(http.request)
        email = request_data.get('email')
        password = request_data.get('password')

        # 2. Kiểm tra dữ liệu hợp lệ
        if not email or not password:
            return json_error('Missing input data', 400)

        # 3. Tìm học viên trong database
        student = http.request.env['portal.student'].sudo().search(
            [('email', '=', email)])

        if not student:
            return json_error('Student not found', 404)

        # 4. Kiểm tra password có đúng không
        if not check_password_hash(student.password_hash, password):
            return json_error('Incorrect password', 400)

        # 5. Tạo access token và refresh token
        payload = {
            'student_id': student.id,
            'student_name': student.name,
            'email': student.email,
        }

        access_token = JWTEncoder.encode_jwt(payload, 'days', 1)
        refresh_token = JWTEncoder.encode_jwt(payload, 'days', 7)

        # 6. Lưu refresh token vào database
        refresh_token_record = http.request.env['portal.student.refresh.token'].sudo().search(
            [('student_id', '=', student.id)])

        if not refresh_token_record:
            http.request.env['portal.student.refresh.token'].sudo().create({
                'student_id': student.id,
                'token': refresh_token,
                'expired_at': datetime.now() + timedelta(days=7),
                'used': False
            })
        else:
            refresh_token_record.write({
                'token': refresh_token,
                'expired_at': datetime.now() + timedelta(days=7),
                'used': False
            })

        # 7. Trả về response với access token và refresh token trong cookies
        response = json_success('Login successful')

        response.set_cookie('access_token', access_token,
                            httponly=True, max_age=60 * 60 * 24)
        response.set_cookie('refresh_token', refresh_token,
                            httponly=True, max_age=60 * 60 * 24 * 7)

        return response
