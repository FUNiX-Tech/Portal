import jwt
import json
import logging
from odoo.http import request
from ..utils.utils import json_response
from ...portal_student_management.utils.jwt_encode import JWTEncoder

logger = logging.getLogger(__name__)


def authentication_validator():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            access_token = request.httprequest.cookies.get("access_token")

            if not access_token:
                return json_response(401, "Unauthorized")
            try:
                decoded_token = JWTEncoder.decode_jwt(access_token)
            except jwt.ExpiredSignatureError:
                return json_response(401, "Expired token")

            except jwt.InvalidTokenError:
                logger.warn(
                    "Some one has submitted with an invalid access token"
                )
                return json_response(403, "Forbidden")
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error")

            if (
                "email" not in decoded_token
                or "student_id" not in decoded_token
                or "student_name" not in decoded_token
            ):
                logger.warn(
                    "Some one has submitted with an invalid access token"
                )
                return json_response(403, "Forbidden")

            student_id = decoded_token["student_id"]

            try:
                student = (
                    request.env["portal.student"]
                    .sudo()
                    .search([("id", "=", student_id)])[0]
                )
                self.student = student
                return origin_function(self, *args, **kwargs)
            except IndexError:
                logger.info(f"Not found student with id {student_id}")
                return json_response(
                    400, f"Not found student with id {student_id}"
                )
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator


def check_match_student():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            payload_student_id = json.loads(request.httprequest.data)[
                "student_id"
            ]
            access_token_student_id = self.student.id

            if (
                self.student.id
                != json.loads(request.httprequest.data)["student_id"]
            ):
                logger.warn(
                    f"SUSPICIOUS BEHAVIOR: student with id {access_token_student_id} has submitted a submission for a student with id {payload_student_id}"
                )
                return json_response(403, "Forbidden")

            return origin_function(self, *args, **kwargs)

        return wrapper

    return decorator


def check_has_assignment():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            assignment_id = request_data.get("assignment_id")

            try:
                assignment = (
                    request.env["assignment"]
                    .sudo()
                    .search([("id", "=", assignment_id)])[0]
                )
                self.assignment = assignment
                return origin_function(self, *args, **kwargs)
            except IndexError:
                logger.info(
                    f"[INFO]: Not found assignment with id {assignment_id}"
                )
                return json_response(
                    400, f"Not found assignment with id {assignment_id}"
                )
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator


def check_student_has_enrolled_course():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            course_id = self.assignment.course.id
            student_id = self.student.id

            try:
                (
                    request.env["course_management"]
                    .sudo()
                    .search(
                        [
                            ("id", "=", course_id),
                            ("student_ids", "in", [student_id]),
                        ]
                    )
                )
                return origin_function(self, *args, **kwargs)

            except IndexError:
                return json_response(
                    400,
                    f"Student with id {student_id} has not enrolled the course with id {course_id}",
                )

            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error")

        return wrapper

    return decorator
