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
        "submission_url", "student_id", "assignment_id"
    )
    @request_validators.check_url("submission_url")
    @assignment_validators.check_has_student()
    @assignment_validators.check_has_assignment()
    @assignment_validators.check_student_has_enrolled_course()
    def submit_submission(self):
        try:
            request_data = json.loads(request.httprequest.data)

            created_submission = (
                request.env["assignment_submission"]
                .sudo()
                .create(
                    {
                        "student": request_data["student_id"],
                        "assignment": request_data["assignment_id"],
                        "submission_url": request_data["submission_url"],
                    }
                )
            )

            response_data = {
                "id": created_submission.id,
                "student": created_submission.student.id,
                "assignment": created_submission.assignment.id,
                "submission_url": created_submission.submission_url,
            }

            return json_response(200, "Submission saved!", response_data)

        except Exception as e:
            logger.error(f"[ERROR]: {str(e)}")
            if str(e) == "'_unknown' object has no attribute 'id'":
                logger.info("WRONG RELATIONAL FIELD!")

            return json_response(500, "Internal Server Error")
