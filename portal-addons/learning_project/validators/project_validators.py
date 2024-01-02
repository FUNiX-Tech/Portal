import jwt
import json
import logging
from odoo.http import request
from odoo.tools import config
from ..utils.utils import json_response
from ...portal_student_management.utils.jwt_encode import JWTEncoder
from ..common import PASSED

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


def check_has_project():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            project_name = request_data.get("project_name")
            course_code = self.course.course_code

            try:
                project = (
                    request.env["project"]
                    .sudo()
                    .search(
                        [
                            ("title", "=", project_name),
                            ("course.course_code", "=", course_code),
                        ]
                    )[0]
                )

                self.project = project
                return origin_function(self, *args, **kwargs)
            except IndexError:
                logger.info(
                    f"[INFO]: Not found project with title {project_name} of course {course_code}"
                )
                return json_response(
                    400,
                    f"Not found project with title {project_name} of course {course_code}",
                )
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator


def check_student_has_enrolled_course():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            course_id = self.project.course.id
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
                    )[0]
                )
                return origin_function(self, *args, **kwargs)

            except IndexError:
                logger.info(
                    f"Student {self.student.email} has not enrolled the course{self.project.course.course_code}"
                )
                return json_response(
                    400,
                    "You haven't enrolled this course.",
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
                    request.env["project_submission"]
                    .sudo()
                    .search(
                        [
                            ("student", "=", self.student.id),
                            ("project", "=", self.project.id),
                        ]
                    )
                ).sorted("id")

                last_submission = (
                    submissions[-1] if len(submissions) > 0 else None
                )

                should_skip = (
                    config.get("allow_to_submit_freely_multiple_times") is True
                    and config.get("debug_mode") is True
                )

                if last_submission and not should_skip:
                    if last_submission.result == PASSED[0]:
                        return json_response(
                            403,
                            "You are not allowed to submit this project because you have already passed this project!",
                        )

                    if last_submission.result == "not_graded":
                        return json_response(
                            403,
                            "You are not allowed to submit this project because the submission is in review!",
                        )

                return origin_function(self, *args, **kwargs)

            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error")

        return wrapper

    return decorator


def skip_authentication():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            email = request_data.get("email")
            course_code = request_data.get("course_code")
            context = {"from_lms": True}

            try:
                student = (
                    request.env["portal.student"]
                    .sudo()
                    .search([("email", "=", email)])
                )

                if not student:
                    body = {
                        "email": email,
                        "name": email.split("@")[0],
                        "username": email.split("@")[0],
                    }

                    created_student = (
                        request.env["portal.student"]
                        .sudo()
                        .with_context(context)
                        .create(body)
                    )

                    request.env["course_management"].sudo().search(
                        [("course_code", "=", course_code)]
                    ).write({"student_ids": [(4, created_student.id)]})

                    self.student = created_student
                else:
                    self.student = student
                return origin_function(self, *args, **kwargs)
            except IndexError as e:
                logger.info(str(e))
                return json_response(
                    400,
                    f"Not found student with email {email}",
                )
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error", str(e))

        return wrapper

    return decorator


def check_has_submission():
    def decorator(origin_function):
        def wrapper(self, *args, **kwargs):
            request_data = json.loads(request.httprequest.data)
            submission_id = request_data.get("submission_id")

            try:
                submission = (
                    request.env["project_submission"]
                    .sudo()
                    .search(
                        [
                            ("id", "=", submission_id),
                            ("student", "=", self.student.id),
                        ]
                    )[0]
                )

                self.submission = submission
                return origin_function(self, *args, **kwargs)
            except IndexError:
                logger.info(f"[INFO]: Not found submission {submission_id}.")
                return json_response(
                    400,
                    "Not found submission.",
                )
            except Exception as e:
                logger.error(str(e))
                return json_response(500, "Internal Server Error.")

        return wrapper

    return decorator
