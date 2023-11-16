import logging
import json
from odoo import http
from odoo.http import request
from ..utils.utils import json_response
from ..validators import request_validators, assignment_validators

logger = logging.getLogger(__name__)


class AssignmentSubmissionController(http.Controller):
    @http.route(
        "/api/v1/assignment/submission",
        type="http",
        auth="public",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    @request_validators.check_fields_presence(
        "submission_url",
        "username",
        "assignment_name",
        "submission_note",
        "course_code",
    )
    @assignment_validators.skip_authentication()
    @request_validators.check_url("submission_url")
    @assignment_validators.check_has_course()
    @assignment_validators.check_has_assignment()
    @assignment_validators.check_student_has_enrolled_course()
    @assignment_validators.check_allowed_to_submit()
    def submit_submission(self):
        try:
            # raise Exception("Test Exception")
            request_data = json.loads(request.httprequest.data)

            created_submission = (
                request.env["assignment_submission"]
                .sudo()
                .create(
                    {
                        "student": self.student.id,
                        "assignment": self.assignment.id,
                        "submission_url": request_data["submission_url"],
                        "submission_note": request_data["submission_note"],
                    }
                )
            )

            assignment = self.assignment

            for criterion in assignment.criteria:
                try:
                    request.env["assignment_criterion_response"].sudo().create(
                        {
                            "submission": created_submission.id,
                            "criterion": criterion.id,
                        }
                    )
                except Exception as e:
                    logger.error(str(e))
                    # uuuv need to handle this exception

            assignment = self.assignment

            response_data = {
                "id": created_submission.id,
                "student": created_submission.student.id,
                "assignment": created_submission.assignment.id,
                "submission_url": created_submission.submission_url,
                "submission_note": created_submission.submission_note,
            }

            # create submission history --> submitted status
            try:
                request.env["submission_history"].sudo().create(
                    {
                        "student_id": self.student.id,
                        "assignment_id": self.assignment.id,
                        "submission_id": created_submission.id,
                        "status": "submitted",  # Đặt trạng thái là 'submitted'
                    }
                )
            except Exception as e:
                logger.error(str(e))
            # end create submission history

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
                        "assignment_id": self.assignment.id,
                        "status": "submission_failed",  # Đặt trạng thái là 'submission_failed'
                    }
                )
            except Exception as e:
                logger.error(str(e))
            # end create submission history

            return json_response(500, "Internal Server Error")

    @http.route(
        "/api/v1/assignment/user",
        type="http",
        auth="public",
        methods=["POST"],
        cors="*",
        csrf=False,
    )
    @assignment_validators.skip_authentication()
    @request_validators.check_fields_presence(
        "course_code", "assignment_name", "username"
    )
    @assignment_validators.check_has_course()
    @assignment_validators.check_has_assignment()
    @assignment_validators.check_student_has_enrolled_course()
    def get_user_assignment(self):
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

            last_submission = submissions[-1] if len(submissions) > 0 else None
            status = (
                "has_not_submitted"
                if last_submission is None
                else last_submission.result
            )
            general_response = (
                ""
                if last_submission is None
                else last_submission.general_response
            )

            response_submissions = []

            for sub in submissions:
                response_submissions.append(
                    {"create_date": sub.create_date.timestamp(), "id": sub.id}
                )

            response_data = {
                "status": status,
                "submissions": response_submissions,
            }

            if last_submission:
                responses = []
                if last_submission.result in ["passed", "did_not_pass"]:
                    for response in last_submission.criteria_responses:
                        responses.append(
                            {
                                "title": response.criterion.title,
                                "result": response.result,
                                "feedback": response.feed_back,
                            }
                        )

                response_data["submission"] = {
                    "date": last_submission.create_date.timestamp(),
                    "general_response": general_response,
                    "responses": responses,
                    "result": last_submission.result,
                    "url": last_submission.submission_url,
                }
            else:
                response_data["submission"] = None

            return json_response(200, "ok", response_data)
        except Exception as e:
            logger.error(str(e))
            return json_response(500, "Internal Server Error")
