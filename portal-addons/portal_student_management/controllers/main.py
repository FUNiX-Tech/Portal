from odoo import http
from werkzeug.security import generate_password_hash, check_password_hash
import re
from ..utils.jwt_encode import JWTEncoder
from datetime import datetime, timedelta
from ..utils.api_utils import (
    json_error,
    json_success,
    get_body_json,
)
from ..middlewares.middlewares import verify_access_token


class StudentAPI(http.Controller):
    @http.route(
        "/api/student/register",
        auth="public",
        method=["POST"],
        type="http",
        cors="*",
        csrf=False,
    )
    def student_register(self, **kwargs):
        """
        Register API - POST /api/student/register
        1. Extract data from request
        2. Validate data
           a. Check missing input
           b. Check email format
           c. Check password format
           d. Check password and password_confirm
        3. Check if email is already registered
        4. Hash password
        5. Create student record
        """
        # 1. Extract data from request
        request_data = get_body_json(http.request)

        # 2. Validate data
        name = request_data.get("name")
        email = request_data.get("email")
        password = request_data.get("password")
        password_confirm = request_data.get("password_confirm")

        # 2a. Check missing input
        if not name or not email or not password or not password_confirm:
            return json_error("Missing input data", 400)

        # 2b. Check email format
        # Regex : https://regex101.com/r/O9oCj8/1
        elif not re.match(r"^[^\.\s][\w\-\.{2,}]+@([\w-]+\.)+[\w-]{2,}$", email):
            return json_error("Invalid email", 400)

        # 2c. Kiểm tra password có đúng định dạng không: https://regex101.com/r/7Hpebb/1

        # password must contain 1 number (0-9)
        # password must contain 1 uppercase letters
        # password must contain 1 lowercase letters
        # password must contain 1 non-alpha numeric number
        # password is 8-32 characters with no space

        elif not re.match(
            r"^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s:])([^\s]){8,32}$", password
        ):
            return json_error("Invalid password", 400)

        # 2d. Check password and password_confirm
        elif password != password_confirm:
            return json_error("Password and confirm password do not match", 400)

        # 3. Check if email is already registered
        student = (
            http.request.env["portal.student"].sudo().search(
                [("email", "=", email)])
        )
        if student:
            return json_error("Email already registered", 400)

        # 4. Hash password
        password_hash = generate_password_hash(password)

        # 5. Create student record
        created_student = (
            http.request.env["portal.student"]
            .sudo()
            .create(
                {
                    "name": name,
                    "email": email,
                    "password_hash": password_hash,
                }
            )
        )

        response = json_success("Student created successfully", 201)

        return response

    @http.route(
        "/api/student/login",
        auth="public",
        methods=["POST"],
        type="http",
        cors="*",
        csrf=False,
    )
    def student_login(self, **kwargs):
        """
        Login API - POST /api/student/login

        1. Extract data from request
        2. Check missing input
        3. Look up student in database to see if student exists
        4. Check if password is correct
        5. Generate access token and refresh token
        6. Save refresh token to database
        7. Return response with access token and refresh token in cookies
        """

        # 1. Extract data from request
        request_data = get_body_json(http.request)
        email = request_data.get("email")
        password = request_data.get("password")

        # 2. Check missing input
        if not email or not password:
            return json_error("Missing input data", 400)

        # 3. Look up student in database to see if student exists
        student = (
            http.request.env["portal.student"].sudo().search(
                [("email", "=", email)])
        )

        if not student:
            return json_error("Student not found", 404)

        # 4. Check if password is correct
        if not check_password_hash(student.password_hash, password):
            return json_error("Incorrect password", 400)

        # 5. Generate access token and refresh token
        payload = {
            "student_id": student.id,
            "student_name": student.name,
            "email": student.email,
        }

        access_token = JWTEncoder.encode_jwt(payload, "days", 1)
        refresh_token = JWTEncoder.encode_jwt(payload, "days", 7)

        # 6. Save refresh token to database
        refresh_token_record = (
            http.request.env["portal.student.refresh.token"]
            .sudo()
            .search([("student_id", "=", student.id)])
        )

        if not refresh_token_record:
            http.request.env["portal.student.refresh.token"].sudo().create(
                {
                    "student_id": student.id,
                    "token": refresh_token,
                    "expired_at": datetime.now() + timedelta(days=7),
                    "used": False,
                }
            )
        else:
            refresh_token_record.write(
                {
                    "token": refresh_token,
                    "expired_at": datetime.now() + timedelta(days=7),
                    "used": False,
                }
            )

        # 7.  Return response with access token and refresh token in cookies
        response = json_success("Login successful")

        response.set_cookie(
            "access_token", access_token, httponly=True, max_age=60 * 60 * 24
        )
        response.set_cookie(
            "refresh_token", refresh_token, httponly=True, max_age=60 * 60 * 24 * 7
        )

        return response

    @http.route(
        "/api/student/refreshAccessToken",
        auth="public",
        methods=["POST"],
        type="http",
        cors="*",
        csrf=False,
    )
    def refresh_access_token(self, **kwargs):
        """
        Refresh token API => POST /api/student/refreshAccessToken

        1. Extract refresh token from cookies
        2. Check if refresh token exists
        3. Decode refresh token to get student_id
        4. Check if refresh token is valid (has email, student_id, student_name)
        5. Look up refresh token in database
        6. Verify if refresh token has been used
        7. Verify if refresh token has expired
        8. Generate new access token
        9. Return response with new access token in cookies
        """

        # 1. Extract refresh token from cookies
        refresh_token = http.request.httprequest.cookies.get("refresh_token")

        # 2. Check if refresh token exists
        if not refresh_token:
            return json_error("Missing refresh token", 400)

        # 3. Decode refresh token to get student_id
        decoded_token = JWTEncoder.decode_jwt(refresh_token)

        # 4. Check if refresh token is valid (has email, student_id, student_name)
        if (
            "email" not in decoded_token
            or "student_id" not in decoded_token
            or "student_name" not in decoded_token
        ):
            return json_error("Invalid refresh token", 400)

        decoded_token["student_id"]

        # 5. Find refresh token in database
        refresh_token_record = (
            http.request.env["portal.student.refresh.token"]
            .sudo()
            .search(
                [
                    ("student_id", "=", decoded_token["student_id"]),
                    ("token", "=", refresh_token),
                ]
            )
        )

        # 6. Verify if refresh token has been used
        if refresh_token_record.used:
            return json_error("Refresh token has been used", 400)

        # 7. Verify if refresh token exists
        if not refresh_token_record:
            return json_error("Invalid refresh token", 400)

        # 7. Verify if refresh token has expired
        now = datetime.now()
        if now > refresh_token_record.expired_at:
            return json_error("Refresh token has expired", 400)

        # REFRESH TOKEN IS VALID
        # 8. Generate new access token

        payload = {
            "student_id": decoded_token["student.id"],
            "student_name": decoded_token["student.name"],
            "email": decoded_token["email"],
        }
        access_token = JWTEncoder.encode_jwt(payload, "days", 1)

        http.request.env["portal.student.refresh.token"].sudo().write({
            "used": True})

        # 9. Return response with new access token in cookies

        response = json_success("Access token refreshed", 200)
        response.set_cookie(
            "access_token", access_token, httponly=True, max_age=60 * 60 * 24
        )

        return response

    @http.route(
        "/api/student/logout",
        auth="public",
        methods=["POST"],
        type="http",
        cors="*",
        csrf=False,
    )
    def student_logout(self, **kwargs):
        """
        Logout API => POST /api/student/logout

        1. Extract access token from cookies
        2. Check if access token exists
        3. Decode access token to get student_id
        4. Check if access token is valid (has email, student_id, student_name)
        5. Delete access token and refresh token in cookies
        7.

        """

        # 1. Extract access token from cookies
        access_token = http.request.httprequest.cookies.get("access_token")

        # 2. Check if access token exists
        if not access_token:
            return json_error("Missing access token", 400)

        # 3. Decode access token to get student_id
        decoded_token = JWTEncoder.decode_jwt(access_token)

        # 4. Check if access token is valid (has email, student_id, student_name)
        if (
            "email" not in decoded_token
            or "student_id" not in decoded_token
            or "student_name" not in decoded_token
        ):
            return json_error("Invalid access token", 400)

        student_id = decoded_token["student_id"]

        # 5. Delete access token and refresh token in cookies
        response = json_success({"message": "Logout successful"})
        response.set_cookie("access_token", "", max_age=0)
        response.set_cookie("refresh_token", "", max_age=0)

        # 6. Delete refresh token in database
        refresh_token_record = (
            http.request.env["portal.student.refresh.token"]
            .sudo()
            .search(
                [
                    ("student_id", "=", student_id),
                ]
            )
        )
        refresh_token_record.write(
            {"token": "", "expired_at": "", "used": False})

        return response

    @http.route(
        "/api/student/edit/<int:student_id>",
        auth="public",
        methods=["POST"],
        type="http",
        cors="*",
        csrf=False,
    )
    @verify_access_token
    def student_edit(self, student_id, **kwargs):
        """
        Edit student API => POST /api/student/edit/<int:student_id>

        1. Verify access token (middleware)
        2. Extract student info from access token
        3. Extract data from request
            a. Check if student_id is in request
            b. Validate input data (phone, gender, date_of_birth)
            c. Check if student_id in request matches student_id in access token
        4. Check if student exists
        5. Update student info

        Note:
        - Date_of_birth is a string in request
        - Only YYYY-MM-DD format is accepted, it will be converted to date in database
        """

        # 1. Verify access token (middleware) and extract decoded_token
        decoded_token = kwargs.get("decoded_access_token", {})

        # 2. Extract data from request
        request_data = get_body_json(http.request)

        # 2a. Check if student_id is in request

        if not student_id:
            return json_error("Missing id", 400)

        # 2b. Validate gender, phone, date_of_birth

        # Gender
        if "gender" in request_data and (
            request_data["gender"] != "male" and request_data["gender"] != "female"
        ):
            return json_error("Invalid input gender", 400)

        # Phone
        if "phone" in request_data and not re.match(r"^\d+$", request_data["phone"]):
            return json_error("Invalid input phone", 400)

        # Date of birth
        if "date_of_birth" in request_data:
            date_of_birth_str = request_data["date_of_birth"]
            try:
                # Convert date_of_birth_str to date
                datetime.strptime(date_of_birth_str, "%Y-%m-%d")
            except ValueError:
                # Return error if date_of_birth_str is not in YYYY-MM-DD format
                return json_error(
                    "Invalid date format for date_of_birth. Expected format: YYYY-MM-DD",
                    400,
                )

        # 2c. Check ìf student_id in request matches student_id in access token
        student_id_request = decoded_token["student_id"]

        if student_id != student_id_request:
            return json_error("Invalid access token", 400)

        # 3. Check if student exists
        student = (
            http.request.env["portal.student"]
            .sudo()
            .search([("id", "=", student_id_request)])
        )

        if not student:
            return json_error("Student not found", 404)

        # 4. Update student info
        fields = ["phone", "name", "gender", "date_of_birth"]

        fields_to_update = {}

        for field in fields:
            if field in request_data:
                fields_to_update[field] = request_data[field]

        if "date_of_birth" in fields_to_update:
            fields_to_update["date_of_birth"] = datetime.strptime(
                fields_to_update["date_of_birth"], "%Y-%m-%d"
            ).date()

        if fields_to_update:
            student.write(fields_to_update)
        else:
            # Return error if no field to update
            return json_error("Missing input", 400)

        response = json_success({"message": "Student updated successfully"})

        return response
