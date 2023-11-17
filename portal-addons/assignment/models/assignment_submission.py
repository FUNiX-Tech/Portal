# -*- coding: utf-8 -*-
"""
Need to set the following variables to config file:
- lms_grade_assignment_url: the lms url to push assignment grading result.
- email_from: sender email (e.g. notification@example.com)
"""

import logging
import requests
from odoo import models, fields, api
from odoo.tools import config

logger = logging.getLogger(__name__)


class AssignmentSubmission(models.Model):
    _name = "assignment_submission"
    _description = "assignment_submission"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    MAIL_SENDER = config.get("email_from")

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    DEFAULT_RESULT = NOT_GRADED[0]

    student = fields.Many2one(
        "portal.student",
        string="Student",
        readonly=True,
        track_visibility=True,
    )
    assignment = fields.Many2one(
        "assignment", string="Assignment", readonly=True
    )
    submission_url = fields.Char(string="Submission Url", readonly=True)
    criteria_responses = fields.One2many(
        "assignment_criterion_response",
        inverse_name="submission",
        string="Criteria",
    )
    result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW],
        required=True,
        string="Result",
        default=DEFAULT_RESULT,
        readonly=True,
    )

    submission_note = fields.Text("Submission Note", readonly=True, default="")
    general_response = fields.Html(string="General Response", default="")

    has_graded_all_criteria = fields.Boolean(
        compute="_has_graded_all_criteria", store=True
    )
    course = fields.Char(related="assignment.course.course_name")
    # ẩn hiện log trace
    # is_show_log_trace = fields.Boolean(string="Show Trace Log", default=False)

    @api.depends("criteria_responses.result", "general_response")
    def _has_graded_all_criteria(self):
        for record in self:
            graded_all = True
            for repsonse in record.criteria_responses:
                if repsonse.result == self.NOT_GRADED[0]:
                    graded_all = False
                    break
            logger.info(record.general_response)
            record.has_graded_all_criteria = (
                graded_all and record.general_response.strip() != ""
            )  # TODO: check empty html general_response

    def submit_grade(self):
        """
        After graded all the criteria, mentor should click the submit button to trigger this function.
        TODO:
            - Calculate and set the final result to the submission according to its criteria.
            - Send notification email to the student.
            - Send notification request to lms.
        """
        for record in self:
            if record.has_graded_all_criteria:
                # Xác định kết quả và gửi mail tương ứng
                # Nếu có bất kỳ criteria nào là 'Unable to review' thì kết quả là 'Unable to review'
                student_email = record.student.email
                assignment_title = record.assignment.title
                course_name = record.assignment.course.course_name
                course_code = record.assignment.course.course_code
                submission_url = record.submission_url

                if any(
                    response.result == self.UNABLE_TO_REVIEW[0]
                    for response in record.criteria_responses
                ):
                    record.result = self.UNABLE_TO_REVIEW[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name}</h2>
                    <h3>Notification of Learning Project Submission result</h3>
                    <p>Assignment: {assignment_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Learning Project Submission is unable to review</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""

                elif any(
                    response.result == self.DID_NOT_PASS[0]
                    for response in record.criteria_responses
                ):
                    record.result = self.DID_NOT_PASS[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name}</h2>
                    <h3>Notification of Learning Project Submission result</h3>
                    <p>Assignment: {assignment_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Learning Project Submission did not pass</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""
                else:
                    record.result = self.PASSED[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name}</h2>
                    <h3>Notification of Learning Project Submission result</h3>
                    <p>Assignment: {assignment_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Learning Project Submission passed</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""

                # send notification email to student
                self.send_email(
                    self,
                    student_email,
                    "Notification of Learning Project Submission result",
                    "Notification of Learning Project Submission result",
                    email_body,
                    "Your description",
                    submission_url,
                    "Go to submission",
                )

                # create submission history --> graded status
                record.env["submission_history"].sudo().create(
                    {
                        "student_id": record.student.id,
                        "assignment_id": record.assignment.id,
                        "submission_id": record.id,
                        "status": "graded",  # Đặt trạng thái là 'graded'
                    }
                )
                # end create submission history

                email_error = self._send_notification_email_to_student()
                lms_error = self._push_grade_result_to_lms()

                error_message = ""
                if email_error != "":
                    error_message += email_error

                if lms_error != "":
                    error_message += lms_error

                if error_message != "":
                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "title": "Error",
                            "message": error_message,
                            "sticky": True,
                        },
                    }

            return True

    def _send_notification_email_to_student(self):
        for record in self:
            try:
                mail_template = self.env.ref(
                    "assignment.submission_result_notification_email_template"
                )
                mail_template.send_mail(
                    self.id, force_send=True, raise_exception=True
                )
                logger.info(
                    f"[Assignment Submission]: Sent notification email to '{record.student.email}'"
                )
                return ""
            except Exception as e:
                logger.error(str(e))
                logger.error(
                    f"[Assignment Submission]: Failed to send notification email to '{record.student.email}'"
                )
                return f"ERROR: Failed to send notification email to '{record.student.email}'"

    def _push_grade_result_to_lms(self):
        for record in self:
            headers = {"Content-Type": "application/json"}
            payload = {
                "assignment_name": record.assignment.title,
                "course_code": record.assignment.course.course_code,
                "email": record.student.email,
                "result": record.result,
            }

            try:
                url = config.get("lms_grade_assignment_url")
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    logger.info("Pushed assignment grading result to LMS")
                    return ""
                else:
                    logger.error(
                        f"Failed to push assignment grading result to LMS: {response.text}"
                    )  # uuuuv TODO: response.text or message?
                    return f"ERROR:Failed to push assignment grading result to LMS: {response.text}"

            except Exception as e:
                logger.error(
                    f"Failed to push assignment grading result to LMS: {str(e)}"
                )
                return f"ERROR:Failed to push assignment grading result to LMS: {str(e)}"

    # method sends email inherits from mail_service
    def send_email(
        self,
        instance_model,
        to_email,
        title,
        subject,
        body,
        description,
        external_link,
        external_text,
        ref_model="assignment.model_assignment_submission",
        email_from="no-reply@funix.edu.vn",
    ):
        self.env["mail_service"].send_email_with_sendgrid(
            self.env["service_key_configuration"],
            to_email,
            "",
            title,
            subject,
            body,
            description,
            external_link,
            external_text,
            ref_model,
            instance_model,
            email_from,
        )
