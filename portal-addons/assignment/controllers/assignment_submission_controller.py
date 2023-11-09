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
    @assignment_validators.authentication_validator()
    @request_validators.check_fields_presence(
        "submission_url", "student_id", "assignment_id"
    )
    @request_validators.check_url("submission_url")
    @assignment_validators.check_match_student()
    @assignment_validators.check_has_assignment()
    @assignment_validators.check_student_has_enrolled_course()
    def submit_submission(self):
        try:
            # raise Exception("Test Exception")
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
            }

            # create submission history --> submitted status

            request.env["submission_history"].sudo().create(
                {
                    "student_id": request_data["student_id"],
                    "assignment_id": request_data["assignment_id"],
                    "submission_id": created_submission.id,
                    "status": "submitted",  # Đặt trạng thái là 'submitted'
                }
            )

            # end create submission history

            return json_response(200, "Submission saved!", response_data)

        except Exception as e:
            logger.info(type(e).__name__)
            logger.error(str(e))
            if str(e) == "'_unknown' object has no attribute 'id'":
                logger.info("WRONG RELATIONAL FIELD!")

            # create submission history --> submission_failed status
            request_data = json.loads(request.httprequest.data)

            request.env["submission_history"].sudo().create(
                {
                    "student_id": request_data["student_id"],
                    "assignment_id": request_data["assignment_id"],
                    "status": "submission_failed",  # Đặt trạng thái là 'submission_failed'
                }
            )
            # end create submission history

            return json_response(500, "Internal Server Error")
