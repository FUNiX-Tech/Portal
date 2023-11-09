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
            payload_username = json.loads(request.httprequest.data)["username"]

            if self.student.email.split("@")[0] != payload_username:
                logger.warn(
                    f"SUSPICIOUS BEHAVIOR: student with email {self.student.email} has submitted a submission for a student with username {payload_username}"
                )
                return json_response(403, "Forbidden")

            return origin_function(self, *args, **kwargs)

        return wrapper

    return decorator


def check_has_course():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            course_code = request_data.get("course_code")

            try:
                course = (
                    request.env["course_management"]
                    .sudo()
                    .search([("course_code", "=", course_code)])[0]
                )
                self.course = course
                return origin_function(self, *args, **kwargs)
            except IndexError:
                logger.info(
                    f"[INFO]: Not found course with code {course_code}"
                )
                return json_response(
                    400, f"Not found course with code {course_code}"
                )
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator


def check_has_assignment():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            assignment_name = request_data.get("assignment_name")
            course_code = self.course.course_code

            try:
                assignment = (
                    request.env["assignment"]
                    .sudo()
                    .search(
                        [
                            ("title", "=", assignment_name),
                            ("course.course_code", "=", course_code),
                        ]
                    )[0]
                )

                self.assignment = assignment
                return origin_function(self, *args, **kwargs)
            except IndexError:
                logger.info(
                    f"[INFO]: Not found assignment with title {assignment_name} of course {course_code}"
                )
                return json_response(
                    400,
                    f"Not found assignment with title {assignment_name} of course {course_code}",
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


def check_allowed_to_submit():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            try:
                submissions = (
                    request.env["assignment_submission"]
                    .sudo()
                    .search(
                        [
                            ("student", "=", self.student.id),
                            ("assignment", "=", self.assignment.id),
                        ]
                    )
                ).sorted("id")

                last_submission = (
                    submissions[-1] if len(submissions) > 0 else None
                )

                if last_submission:
                    if last_submission.result == "passed":
                        return json_response(
                            403,
                            "You are not allowed to submit this assignment because you have already passed this assignment!",
                        )

                    if last_submission.result == "not_graded":
                        return json_response(
                            403,
                            "You are not allowed to submit this assignment because the submission is in review!",
                        )

                return origin_function(self, *args, **kwargs)

            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error")

        return wrapper

    return decorator
