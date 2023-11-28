import re
import json
import logging
from odoo.http import request
from ..utils.utils import json_response

logger = logging.getLogger(__name__)


def check_url(*url_fields):
    """
    Decorator validate url_field
    """

    def decorator(origin_function):
        def wrapper(*args, **kwargs):
            request_data = json.loads(request.httprequest.data)

            for url_field in url_fields:
                if url_field in list(request_data.keys()):
                    url = request_data.get(url_field)
                    if not isinstance(url, str):
                        return json_response(
                            400, _invalid_field_template(url_field, url)
                        )
                    regex = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

                    localhost_regex = "^http:\\/\\/localhost.*$"

                    if not re.match(
                        regex, url, re.IGNORECASE
                    ) and not re.match(localhost_regex, url, re.IGNORECASE):
                        return json_response(
                            400, _invalid_field_template(url_field, url)
                        )

            return origin_function(*args, **kwargs)

        return wrapper

    return decorator


def check_ticket_category(category_field):
    """
    Creates a decorator that checks if the provided 'category_field' is valid.
    KeyError: If the 'category_field' is missing from the request data.
    """

    def decorator(origin_function):
        def wrapper(*args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            category = request_data.get(category_field)
            if category not in [
                "outdated",
                "bad_explain",
                "insufficient_details",
                "broken_resource",
                "error_translation",
            ]:
                return json_response(
                    400,
                    _invalid_field_template(
                        "category_field",
                        category,
                        "category must be one of the following: outdated, bad_explain, insufficient_details, broken_resource, error_translation",
                    ),
                )
            return origin_function(*args, **kwargs)

        return wrapper

    return decorator


def check_student(student_field):
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            data = json.loads(request.httprequest.data)
            student_email = data.get(student_field)
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
                        f"[INFO]: Not found student with code {student_email}"
                    )
                    return json_response(
                        400,
                        {
                            "message": f"Not found course with code {student_email}"
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
            data = json.loads(request.httprequest.data)
            course_code = data.get(course_field)
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
            request_data = json.loads(request.httprequest.data)
            request_fields = list(request_data.keys())

            for field in required_fields:
                if field not in request_fields:
                    return json_response(400, _missing_field_template(field))
            return origin_function(*args, **kwargs)

        return wrapper

    return decorator


def _missing_field_template(field):
    return {"message": f"Missing field: '{field}'"}


def _invalid_field_template(field_name, field_value, requirement=""):
    message = f"Invalid field: '{field_name}': '{field_value}'."

    if requirement != "":
        message += f" Required: {requirement}."

    return {"message": message}
