import re
import json
import logging
from odoo.http import request
from ..utils.utils import json_response

logger = logging.getLogger(__name__)


def check_student(student_field):
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            if request.httprequest.method == "POST":
                data = json.loads(request.httprequest.data)
                student_email = data.get(student_field)
            elif request.httprequest.method == "GET":
                student_email = request.params.get(student_field)
            try:
                student = (
                    request.env["portal.student"]
                    .sudo()
                    .search([("email", "=", student_email)])
                )
                if student:
                    self.student = student
                    return origin_function(self, *args, **kwargs)
                else:
                    logger.info(
                        f"[INFO]: Not found student with email {student_email}"
                    )
                    return json_response(
                        400,
                        {
                            "message": f"Not found student with email {student_email}"
                        },
                    )
            except Exception as e:
                logger.error(str(e))
                return json_response(
                    500, {"message": "Internal Server Error."}
                )

        return wrapper

    return decorator


def check_has_course(course_field):
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            if request.httprequest.method == "POST":
                data = json.loads(request.httprequest.data.decode("utf-8"))
                course_code = data.get(course_field)
            elif request.httprequest.method == "GET":
                course_code = request.params.get(course_field).replace(
                    " ", "+"
                )  # If in url query params contain "+" it will be replaced by " ". So that we need to revert it before proceeding
            try:
                course = (
                    request.env["course_management"]
                    .sudo()
                    .search([("course_code", "=", course_code)])
                )
                if course:
                    self.course = course
                    return origin_function(self, *args, **kwargs)
                else:
                    logger.info(
                        f"[INFO]: Not found course with code {course_code}"
                    )
                    return json_response(
                        400,
                        {
                            "message": f"Not found course with code {course_code}"
                        },
                    )
            except Exception as e:
                logger.error(str(e))
                return json_response(
                    500, {"message": "Internal Server Error."}
                )

        return wrapper

    return decorator


def check_fields_presence(*required_fields):
    """
    Decorator validate có thiếu field nào trong body POST request không.
    Return Http Response 400 nếu invalid.
    """

    def decorator(origin_function):
        def wrapper(*args, **kwargs):
            if request.httprequest.method == "POST":
                request_data = json.loads(request.httprequest.data)
                request_fields = list(request_data.keys())
            elif request.httprequest.method == "GET":
                request_data = request.params
                request_fields = list(request_data.keys())
            for field in required_fields:
                if field not in request_fields:
                    return json_response(400, _missing_field_template(field))
            return origin_function(*args, **kwargs)

        return wrapper

    return decorator


def _missing_field_template(field):
    return {"message": f"Missing field: '{field}'"}
