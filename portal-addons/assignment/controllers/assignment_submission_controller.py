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
        "email",
        "assignment_name",
        "submission_note",
        "course_code",
    )
    @assignment_validators.skip_authentication()
    @request_validators.check_url("submission_url")
    @assignment_validators.check_has_course()
    @assignment_validators.check_has_assignment()
    @assignment_validators.check_student_has_enrolled_course()
    # @assignment_validators.check_allowed_to_submit() # uuuuv
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

                # send mail to student
                # lấy thông tin AssignmentSubmission và student như:
                # student email, assignment title, course name, course code, submission_url
                student_email = self.student.email
                assignment_title = self.assignment.title
                course_name = self.assignment.course.course_name
                course_code = self.assignment.course.course_code
                submission_url = created_submission.submission_url

                # Tạo nội dung email
                body = f"""<div>
                <h2>Hello {self.student.name}</h2>
                <h3>You had submitted Learning Project Submission successfully </h3>
                <p>Assignment: {assignment_title}</p>
                <p>Course name: {course_name}</p>
                <p>Couse code: {course_code}</p>
                <p>I hope you happy with that</p>
                <strong>Thank you!</strong>
                <div>"""

                # Gửi email
                created_submission.send_email(
                    created_submission,
                    student_email,
                    "Learning Project Submission Submitted Successfully",
                    "Notification of Learning Project Submission Module",
                    body,
                    "Your description",
                    submission_url,
                    "Go to Learning Project Submission",
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
        "course_code", "assignment_name", "email"
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

            # get submission
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
                "is_last_submission": submission.id == last_submission.id,
            }

            if submission:
                responses = []
                if submission.result in ["passed", "did_not_pass"]:
                    for response in submission.criteria_responses:
                        responses.append(
                            {
                                "title": response.criterion.title,
                                "result": response.result,
                                "feedback": response.feed_back,
                            }
                        )

                response_data["submission"] = {
                    "date": submission.create_date.timestamp(),
                    "general_response": general_response,
                    "responses": responses,
                    "result": submission.result,
                    "id": submission.id,
                    "url": submission.submission_url,
                }
            else:
                response_data["submission"] = None

            return json_response(200, "ok", response_data)
        except Exception as e:
            logger.error(str(e))
            return json_response(500, "Internal Server Error")
