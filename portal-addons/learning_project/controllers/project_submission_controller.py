import logging
import json
from odoo import http
from odoo.http import request
from ..utils.utils import json_response
from ..validators import request_validators, project_validators
from odoo.addons.portal_student_management.middlewares.middlewares import (
    verify_access_token,
)
from datetime import datetime
from ..common import PASSED, DID_NOT_PASS, NOT_GRADED, CANCELED

logger = logging.getLogger(__name__)


class ProjectSubmissionController(http.Controller):
    @http.route(
        "/api/v1/project/submission",
        type="http",
        auth="public",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    # @verify_access_token
    @request_validators.check_fields_presence(
        "submission_url",
        "email",
        "project_name",
        "submission_note",
        "course_code",
    )
    @project_validators.skip_authentication()
    @request_validators.check_url("submission_url")
    @project_validators.check_has_course()
    @project_validators.check_has_project()
    @project_validators.check_student_has_enrolled_course()
    @project_validators.check_allowed_to_submit()
    def submit_submission(self, *args, **kwargs):
        try:
            request_data = json.loads(request.httprequest.data)

            created_submission = (
                request.env["project_submission"]
                .sudo()
                .create(
                    {
                        "student": self.student.id,
                        "project": self.project.id,
                        "submission_url": request_data["submission_url"],
                        "submission_note": request_data["submission_note"],
                    }
                )
            )

            project = self.project

            for criterion in project.criteria:
                try:
                    request.env["project_criterion_response"].sudo().create(
                        {
                            "submission": created_submission.id,
                            "criterion": criterion.id,
                        }
                    )
                except Exception as e:
                    logger.error(str(e))
                    # uuuv need to handle this exception

            response_data = {
                "id": created_submission.id,
                "student": created_submission.student.id,
                "project": created_submission.project.id,
                "submission_url": created_submission.submission_url,
                "submission_note": created_submission.submission_note,
            }

            # create submission history --> submitted status
            try:
                request.env["submission_history"].sudo().create(
                    {
                        "student_id": self.student.id,
                        "project_id": self.project.id,
                        "submission_id": created_submission.id,
                        "status": "submitted",  # Đặt trạng thái là 'submitted'
                    }
                )

                # send mail to student
                # lấy thông tin ProjectSubmission và student như:
                # student email, project title, course name, course code, submission_url
                student_email = self.student.email
                project_title = self.project.title
                course_name = self.project.course.course_name
                course_code = self.project.course.course_code
                submission_url = created_submission.submission_url

                # Tạo nội dung email
                body = f"""<div>
                <h2>Hello {self.student.name}</h2>
                <h3>You had successfully submitted Project Submission  </h3>
                <p>Project: {project_title}</p>
                <p>Course name: {course_name}</p>
                <p>Couse code: {course_code}</p>
                <p>I hope you happy with that</p>
                <strong>Thank you!</strong>
                <div>"""

                # Gửi email
                created_submission.send_email(
                    created_submission,
                    student_email,
                    "Notification:  Project Submission Successfully Submitted",
                    "Notification:  Project Submission Successfully Submitted",
                    body,
                    "Project Submission Submitted Successfully",
                    submission_url,
                    "Go to Project Submission",
                )

            except Exception as e:
                logger.error(str(e))
            # end create submission history

            # assign to mentor
            try:
                last_submission = (
                    request.env["project_submission"]
                    .sudo()
                    .search(
                        [
                            ("student", "=", self.student.id),
                            ("project", "=", self.project.id),
                            ("result", "!=", CANCELED[0]),
                        ]
                    )
                ).sorted("id")[0]
                created_submission.mentor_id = last_submission.mentor_id
            except IndexError:
                pass
            except Exception as e:
                logger.error(str(e))

            return json_response(200, "Submission saved!", response_data)

        except Exception as e:
            logger.info(type(e).__name__)
            logger.error(str(e))
            if str(e) == "'_unknown' object has no attribute 'id'":
                logger.info("WRONG RELATIONAL FIELD!")

            # create submission history --> submission_failed status
            try:
                request.env["submission_history"].sudo().create(
                    {
                        "student_id": self.student.id,
                        "project_id": self.project.id,
                        "status": "submission_failed",  # Đặt trạng thái là 'submission_failed'
                    }
                )
            except Exception as e:
                logger.error(str(e))
            # end create submission history

            return json_response(500, "Internal Server Error")

    @http.route(
        "/api/v1/project/user",
        type="http",
        auth="public",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    # @verify_access_token
    @project_validators.skip_authentication()
    @request_validators.check_fields_presence(
        "course_code", "project_name", "email"
    )
    @project_validators.check_has_course()
    @project_validators.check_has_project()
    @project_validators.check_student_has_enrolled_course()
    def get_user_project(self):
        try:
            submissions = (
                request.env["project_submission"]
                .sudo()
                .search(
                    [
                        ("student", "=", self.student.id),
                        ("project", "=", self.project.id),
                        ("result", "!=", CANCELED[0]),
                    ]
                )
            ).sorted("id")

            submission = None

            request_data = json.loads(request.httprequest.data)
            submission_id = request_data.get("submission_id")

            last_submission = submissions[-1] if len(submissions) > 0 else None

            if submission_id is None:
                submission = last_submission
            else:
                filtered_submission = submissions.filtered(
                    lambda s: s.id == submission_id
                )

                if filtered_submission:
                    submission = filtered_submission[0]
                else:
                    return json_response(
                        400, f"Not found submsision with id {submission_id}"
                    )

            status = (
                "has_not_submitted"
                if submission is None
                else submission.result
            )
            general_response = (
                "" if submission is None else submission.general_response
            )

            response_submissions = []

            for sub in submissions:
                response_submissions.append(
                    {"create_date": sub.create_date.timestamp(), "id": sub.id}
                )

            response_data = {
                "status": status,
                "submissions": response_submissions,
                "is_last_submission": submission.id == last_submission.id
                if submission is not None
                else False,
            }

            if submission:
                responses = []
                if submission.result in [PASSED[0], DID_NOT_PASS[0]]:
                    for response in submission.criteria_responses:
                        responses.append(
                            {
                                "title": response.criterion.title,
                                "result": response.result,
                                "feedback": response.feedback,
                                "number": response.number,
                                "criteria_group": response.criteria_group.title,
                                "group_number": response.criteria_group.number,
                                "specifications": response.criterion.sumarized_content,
                            }
                        )

                response_data["submission"] = {
                    "date": submission.create_date.timestamp(),
                    "general_response": general_response,
                    "responses": ProjectSubmissionController._serialize_criteria(
                        responses
                    ),
                    "result": submission.result,
                    "url": submission.submission_url,
                    "id": submission.id,
                }
            else:
                response_data["submission"] = None

            return json_response(200, "ok", response_data)
        except Exception as e:
            logger.error(str(e))
            return json_response(500, "Internal Server Error")

    @classmethod
    def _serialize_criteria(cls, criteria):
        groups = {}

        criteria.sort(key=lambda e: e["group_number"])
        for item in criteria:
            if groups.get(item.get("criteria_group")) is None:
                groups[item.get("criteria_group")] = []

            groups[item.get("criteria_group")].append(item)

        output = []

        for key in groups.keys():
            groups[key].sort(key=lambda e: e["number"])
            output.append({"group_name": key, "criteria": groups[key]})

        return output

    @http.route(
        "/api/v1/project/submission/cancel",
        type="http",
        auth="public",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    @request_validators.check_fields_presence("submission_id", "email")
    @project_validators.skip_authentication()
    @project_validators.check_has_submission()
    def cancel_project_submission(self):
        try:
            submission = self.submission

            if submission.result == CANCELED[0]:
                return json_response(
                    400, "This submission has already canceled."
                )

            if submission.result != NOT_GRADED[0]:
                return json_response(
                    400,
                    "You cannot cancel this submission because the submission has been graded.",
                )

            minutes = round(
                (datetime.now() - submission.create_date).total_seconds() / 60
            )
            if minutes > 30:
                return json_response(
                    400,
                    "You cannot cancel this submission because it was submitted more than 30 minutes ago.",
                )

            if submission.mentor_id.id is not False:
                return json_response(
                    400,
                    "You cannot cancel this submission because a mentor is reviewing it.",
                )

            submission.result = CANCELED[0]

            try:
                request.env["submission_history"].sudo().create(
                    {
                        "student_id": self.student.id,
                        "project_id": self.project.id,
                        "submission_id": submission.id,
                        "status": "submission_cancelled",  # Đặt trạng thái là 'submission_cancelled'
                    }
                )

                # send mail to student
                # lấy thông tin ProjectSubmission và student như:
                # student email, project title, course name, course code, submission_url
                student_email = self.student.email
                project_title = self.project.title
                course_name = self.project.course.course_name
                course_code = self.project.course.course_code
                submission_url = submission.submission_url

                # Tạo nội dung email
                body = f"""<div>
                <h2>Hello {self.student.name}</h2>
                <h3>You had successfully canceled Project Submission  </h3>
                <p>Project: {project_title}</p>
                <p>Course name: {course_name}</p>
                <p>Couse code: {course_code}</p>
                <div>"""

                # Gửi email
                submission.send_email(
                    submission,
                    student_email,
                    "Notification:  Project Submission Successfully Canceled",
                    "Notification:  Project Submission Successfully Canceled",
                    body,
                    "Project Submission Canceled Successfully",
                    submission_url,
                    "Go to Project Submission",
                )

            except Exception as e:
                logger.error(str(e))

            return json_response(200, "Canceled submission successfully.")

        except Exception as e:
            logger.error(str(e))
            return json_response(500, "Internal Server Error")
