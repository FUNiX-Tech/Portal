# flake8: noqa
from odoo import http
from ..utils.api_utils import (
    json_error,
    json_success,
    get_body_json,
)


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
        2a. Check missing input
        3. Create student record
        """
        # 1. Extract data from request
        request_data = get_body_json(http.request)

        # 2. Validate data
        name = request_data.get("name")
        email = request_data.get("email")
        student_code = request_data.get("student_code")
        username = request_data.get("username")

        # 2a. Check missing input
        if not name or not email or not student_code or not username:
            return json_error("Missing input data", 400)

        # 3. Create student record
        http.request.env["portal.student"].with_context(
            "from_lms"
        ).sudo().create(
            {
                "name": name,
                "email": email,
                "student_code": student_code,
                "username": username,
            }
        )

        response = json_success("Student created successfully", 201)

        return response
