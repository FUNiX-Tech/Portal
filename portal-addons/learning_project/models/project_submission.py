# -*- coding: utf-8 -*-
"""
Need to set the following variables to config file:
- lms_grade_project_url: the lms url to push project grading result.
- email_from: sender email (e.g. notification@example.com)
"""

import logging
import requests
from odoo import models, fields, api
from odoo.tools import config
from odoo.addons.website.tools import text_from_html

logger = logging.getLogger(__name__)


class ProjectSubmission(models.Model):
    _name = "project_submission"
    _description = "project_submission"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    MAIL_SENDER = config.get("email_from")

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    INCOMPLETE = ("incomplete", "Incomplete")
    DEFAULT_RESULT = NOT_GRADED[0]

    student = fields.Many2one(
        "portal.student",
        string="Student",
        readonly=True,
        track_visibility=True,
    )
    project = fields.Many2one("project", string="Project", readonly=True)
    submission_url = fields.Char(string="Submission Url", readonly=True)
    criteria_responses = fields.One2many(
        "project_criterion_response",
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
    annotation = fields.Html(string="Annotation", default="")
    has_graded_all_criteria = fields.Boolean(
        compute="_has_graded_all_criteria", store=True
    )
    course = fields.Char(related="project.course.course_name")
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

                for component in repsonse.feedback_components:
                    if (
                        component.is_show is True
                        and component.is_optional is False
                        and text_from_html(component.content).strip() == ""
                    ):
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
            # Chưa nhập nhận xét tổng thì không cho submit + thông báo
            if text_from_html(record.general_response).strip() == "":
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Error",
                        "message": "General response must not be empty!",
                        "sticky": True,
                    },
                }

            is_unable_to_review = self.env.context.get("unable_to_review")
            if record.has_graded_all_criteria or is_unable_to_review:
                # Xác định kết quả và gửi mail tương ứng
                # Nếu có bất kỳ criteria nào là 'Unable to review' thì kết quả là 'Unable to review'
                student_email = record.student.email
                project_title = record.project.title
                course_name = record.project.course.course_name
                course_code = record.project.course.course_code
                submission_url = record.submission_url

                if is_unable_to_review:
                    record.result = self.UNABLE_TO_REVIEW[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name}</h2>
                    <h3>Notification of Project Submission result</h3>
                    <p>Project: {project_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Project Submission is unable to review</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""

                elif any(
                    response.result
                    in [self.DID_NOT_PASS[0], self.INCOMPLETE[0]]
                    for response in record.criteria_responses
                ):
                    record.result = self.DID_NOT_PASS[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name}</h2>
                    <h3>Notification of Project Submission result</h3>
                    <p>Project: {project_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Project Submission did not pass</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""
                else:
                    record.result = self.PASSED[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name}</h2>
                    <h3>Notification of Project Submission result</h3>
                    <p>Project: {project_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Project Submission passed</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""

                # send notification email to student
                self.send_email(
                    self,
                    student_email,
                    "Notification of Project Submission result",
                    "Notification of Project Submission result",
                    email_body,
                    "Your description",
                    submission_url,
                    "Go to submission",
                )

                # create submission history --> graded status
                record.env["submission_history"].sudo().create(
                    {
                        "student_id": record.student.id,
                        "project_id": record.project.id,
                        "submission_id": record.id,
                        "status": "graded",  # Đặt trạng thái là 'graded'
                    }
                )
                # end create submission history

                error_message = self._push_grade_result_to_lms()

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

    def _push_grade_result_to_lms(self):
        # Dành cho local dev
        # nếu odoo config DEBUG == True và SKIP_PUSH_GRADE_TO_LMS == True thì bỏ qua bước này
        should_skip = (
            config.get("skip_push_grade_to_lms") is True
            and config.get("debug_mode") is True
        )
        if should_skip:
            logger.info(
                "DEBUG MODE: skip PUSH GRADE TO LMS error because of debug_mode is True and skip_push_grade_to_lms is True"
            )
            return ""

        for record in self:
            headers = {"Content-Type": "application/json"}
            payload = {
                "project_name": record.project.title,
                "course_code": record.project.course.course_code,
                "email": record.student.email,
                "result": record.result,
            }

            try:
                url = config.get("lms_grade_project_url")
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    logger.info("Pushed project grading result to LMS")
                    return ""
                else:
                    logger.error(
                        f"Failed to push project grading result to LMS: {response.text}"
                    )

                    return f"ERROR:Failed to push project grading result to LMS: {response.text}"

            except Exception as e:
                logger.error(
                    f"Failed to push project grading result to LMS: {str(e)}"
                )
                return f"ERROR:Failed to push project grading result to LMS: {str(e)}"

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
        ref_model="learning_project.model_project_submission",
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
