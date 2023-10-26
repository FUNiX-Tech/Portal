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

    @http.route('/api/student/refreshAccessToken', auth='public', methods=['POST'], type='http', cors='*', csrf=False)
    def refresh_access_token(self, **kwargs):
        """
        API để refresh access token

        1. Lấy refresh token từ cookies
        2. Kiểm tra refresh token có tồn tại không
        3. Decode refresh token để lấy student_id
        4. Kiểm tra thông tin trong refresh token có đầy đủ không
        5. Tìm refresh token trong database
        6. Kiểm tra refresh token đã sử dụng chưa
        7. Kiểm tra refresh token có hết hạn không
        8. Tạo access token mới
        9. Trả về response với access token mới
        """

        # 1. Lấy refresh token từ cookies
        refresh_token = http.request.httprequest.cookies.get('refresh_token')

        # 2. Kiểm tra refresh token có tồn tại không
        if not refresh_token:
            return json_error('Missing refresh token', 400)

        # 3. Decode refresh token để lấy student_id
        decoded_token = JWTEncoder.decode_jwt(refresh_token)

        # 4. Kiểm tra thông tin trong refresh token có đầy đủ không
        if 'email' not in decoded_token or 'student_id' not in decoded_token or 'student_name' not in decoded_token:
            return json_error('Invalid refresh token', 400)

        decoded_token['student_id']

        # 5. Tìm refresh token trong database
        refresh_token_record = http.request.env['portal.student.refresh.token'].sudo().search([
            ('student_id', '=', decoded_token['student_id']),
            ('token', '=', refresh_token),
        ])

        # 6. Kiểm tra refresh token đã sử dụng chưa
        if refresh_token_record.used:
            return json_error('Refresh token has been used', 400)

        # 7. Kiểm tra refresh token có hết hạn không
        if not refresh_token_record:
            return json_error('Invalid refresh token', 400)

        now = datetime.now()
        if now > refresh_token_record.expired_at:
            return json_error('Refresh token has expired', 400)

        # REFRESH TOKEN HỢP LỆ
        # 8. Tạo access token mới

        payload = {
            'student_id': decoded_token['student.id'],
            'student_name': decoded_token['student.name'],
            'email': decoded_token['email'],
        }
        access_token = JWTEncoder.encode_jwt(payload, 'days', 1)

        http.request.env['portal.student.refresh.token'].sudo().write({
            'used': True})

        # 9. Trả về response với access token mới

        response = json_success('Access token refreshed', 200)
        response.set_cookie('access_token', access_token,
                            httponly=True, max_age=60 * 60 * 24)

        return response

    @http.route('/api/student/logout', auth='public', methods=['POST'], type='http', cors='*', csrf=False)
    def student_logout(self, **kwargs):
        """
        API để logout học viên

        1. Lấy access token từ cookies
        2. Kiểm tra access token có tồn tại không
        3. Decode access token để lấy student_id
        4. Kiểm tra thông tin trong access token có đầy đủ không
        5. Tìm refresh token trong database
        6. Xóa refresh token trong database
        7. Trả về response và clear access token và refresh token trong cookies

        """

        # 1. Lấy access token từ cookies
        access_token = http.request.httprequest.cookies.get('access_token')

        # 2. Kiểm tra access token có tồn tại không
        if not access_token:
            return json_error('Missing access token', 400)

        # 3. Decode access token để lấy student_id
        decoded_token = JWTEncoder.decode_jwt(access_token)

        # 4. Kiểm tra thông tin trong access token có đầy đủ không
        if 'email' not in decoded_token or 'student_id' not in decoded_token or 'student_name' not in decoded_token:
            return json_error('Invalid access token', 400)

        student_id = decoded_token['student_id']

        # 5. Xóa access token và refresh token trong cookies
        response.set_cookie('access_token', '', max_age=0)
        response.set_cookie('refresh_token', '', max_age=0)

        # 6. Xóa refresh token trong database
        refresh_token_record = http.request.env['portal.student.refresh.token'].sudo().search([
            ('student_id', '=', student_id),
        ])
        refresh_token_record.write({
            'token': '',
            'expired_at': '',
            'used': False
        })
        response = json_response({'message': 'Logout successful'})

        return response
