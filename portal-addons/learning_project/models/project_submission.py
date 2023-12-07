# -*- coding: utf-8 -*-
"""
- lms_grade_project_url: the lms url to push project grading result retrieve from config key module
Need to set the following variables to config file:
- email_from: sender email (e.g. notification@example.com)
"""

import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import config
from odoo.addons.website.tools import text_from_html
from ..common import (
    NOT_GRADED,
    CANCELED,
    PASSED,
    DID_NOT_PASS,
    UNABLE_TO_REVIEW,
    INCOMPLETE,
)

logger = logging.getLogger(__name__)


class ProjectSubmission(models.Model):
    _name = "project_submission"
    _description = "project_submission"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
        [NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW, CANCELED],
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

    course = fields.Char(related="project.course.course_name")

    lms_grade_update_status = fields.Char(
        string="LMS Grade Update LMS", default="Idle"
    )

    approved = fields.Boolean(string="Approved", default=False)

    has_abnormal_result = fields.Boolean(
        string="Has Abnormal Result",
        compute="_compute_has_abnormal_result",
    )

    should_display_approve_btn = fields.Boolean(
        string="Should display approve button",
        compute="_compute_should_display_approve_btn",
    )

    @api.depends(
        "criteria_responses.result",
        "criteria_responses.step",
        "general_response",
    )
    def _has_graded_all_criteria(self):
        for record in self:
            graded_all = True
            for response in record.criteria_responses:
                if (
                    response.result == NOT_GRADED[0]
                    or response.step < 4
                    or text_from_html(response.feedback).strip() == ""
                ):
                    graded_all = False
                    break

            record.has_graded_all_criteria = (
                graded_all
                and text_from_html(record.general_response).strip() != ""
            )

    def submit_grade(self):
        """
        After graded all the criteria, mentor should click the submit button to trigger this function.
        TODO:
            - Calculate and set the final result to the submission according to its criteria.
            - check if any abnormal result. If there is:
                + Send notification email to admin
                + Waiting for approving to grade
            - Otherwise:
                + Send notification email to the student.
                + Send notification request to lms.
        """

        for record in self:
            # Chưa nhập nhận xét tổng thì không cho submit + thông báo
            if text_from_html(record.general_response).strip() == "":
                raise UserError("Missing general response.")

            is_unable_to_review = self.env.context.get("unable_to_review")

            # Kiểm tra kết quả bất thường
            if (
                record.has_abnormal_result
                and record.approved is False
                and not is_unable_to_review
            ):
                record.lms_grade_update_status = "waiting_for_approving"
                admin_email = "vuntafx17889@funix.edu.vn"
                email_body = f"""<div>
                    <h2>Hello Admin,</h2>
                    <h3 style="color: red;"><strong>There is an abnormal grading result!</strong></h3>
                    <p>Project: {record.project.title}</p>
                    <p>Course name: {record.project.course.course_name}</p>
                    <p>Course code: {record.project.course.course_code}</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {record.submission_url}</p>
                    </div>"""
                self.send_email(
                    self,
                    admin_email,
                    "Notification: Abnormal Project Grading Result",
                    "Notification: Abnormal Project Grading Result",
                    email_body,
                    "Notification: Abnormal Project Grading Result",
                    record.submission_url,
                    "Go to Project Submission",
                )

                # Thông báo cho mentor về việc này
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Notification",
                        "message": "This is an abnormal project grading result. An email was sent to admin. You'll get notification email when we're done with checking it.",
                        "sticky": True,
                    },
                }

            if record.approved is False:
                record.approved = True

            if record.has_graded_all_criteria or is_unable_to_review:
                # Xác định kết quả và gửi mail tương ứng
                # Nếu có bất kỳ criteria nào là 'Unable to review' thì kết quả là 'Unable to review'
                student_email = record.student.email
                project_title = record.project.title
                course_name = record.project.course.course_name
                course_code = record.project.course.course_code
                submission_url = record.submission_url

                if is_unable_to_review:
                    record.result = UNABLE_TO_REVIEW[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name},</h2>
                    <p>Project: {project_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Unable to review</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <strong>Thank you!</strong>
                    </div>"""

                elif any(
                    response.result in [DID_NOT_PASS[0], INCOMPLETE[0]]
                    for response in record.criteria_responses
                ):
                    record.result = DID_NOT_PASS[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name},</h2>
                    <p>Project: {project_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Did not pass</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <strong>Thank you!</strong>
                    </div>"""
                else:
                    record.result = PASSED[0]
                    email_body = f"""<div>
                    <h2>Hello {record.student.name},</h2>
                    <p>Project: {project_title}</p>
                    <p>Course name: {course_name}</p>
                    <p>Course code: {course_code}</p>
                    <p>Result: Passed</p>
                    <p>Submission Note: {record.submission_note}</p>
                    <p>General Response: {record.general_response}</p>
                    <p>Submission Url: {submission_url}</p>
                    <strong>Thank you!</strong>
                    </div>"""

                # send notification email to student
                self.send_email(
                    self,
                    student_email,
                    "Notification: Project Submission Results Available",
                    "Notification: Project Submission Results Available",
                    email_body,
                    "Notification: Project Submission Results Available",
                    submission_url,
                    "Go to Project Submission",
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
                # email_error = self._send_notification_email_to_student()
                lms_error = self._push_grade_result_to_lms()
                error_message = ""
                # if email_error != "":
                #     error_message += email_error
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

    def _push_grade_result_to_lms(self):
        for record in self:
            # Dành cho local dev
            # nếu odoo config DEBUG_MODE == True và SKIP_PUSH_GRADE_TO_LMS == True thì bỏ qua bước này
            should_skip = (
                config.get("skip_push_grade_to_lms") is True
                and config.get("debug_mode") is True
            )
            if should_skip:
                record.lms_grade_update_status = "Updated"
                logger.info(
                    "DEBUG MODE: skip PUSH GRADE TO LMS error because of debug_mode is True and skip_push_grade_to_lms is True"
                )
                return ""
            headers = {"Content-Type": "application/json"}
            payload = {
                "project_name": record.project.title,
                "course_code": record.project.course.course_code,
                "email": record.student.email,
                "result": record.result,
            }

            try:
                url = self.env[
                    "service_key_configuration"
                ].get_api_key_by_service_name("LMS_PUSH_GRADE_URL")

                if not url:
                    return "Missing LMS_PUSH_GRADE_URL"

                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    record.lms_grade_update_status = "Updated"
                    logger.info("Pushed project grading result to LMS")
                    return ""
                else:
                    record.lms_grade_update_status = f"Error: {response.text}"
                    logger.error(
                        f"Failed to push project grading result to LMS: {response.text}"
                    )

                    return f"ERROR:Failed to push project grading result to LMS: {response.text}"

            except Exception as e:
                record.lms_grade_update_status = f"Error: {str(e)}"
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

    def re_update_lms_grade(self):
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

    @classmethod
    def _send_notification_email_to_admin():
        pass

    @api.depends("criteria_responses.is_abnormal_result")
    def _compute_has_abnormal_result(self):
        for record in self:
            has_abnormal_result = False
            for c in record.criteria_responses:
                if c.is_abnormal_result is True:
                    has_abnormal_result = True
                    break

            record.has_abnormal_result = has_abnormal_result

    def button_approve(self):
        for record in self:
            record.approved = True

        mentor_email = record.mentor_id.email
        email_body = f"""<div>
            <h2>Hello Admin,</h2>
            <h3 style="color: red;"><strong>Admin Approved Your Project Grading Result!</strong></h3>
            <p>Project: {record.project.title}</p>
            <p>Course name: {record.project.course.course_name}</p>
            <p>Course code: {record.project.course.course_code}</p>
            <p>Submission Note: {record.submission_note}</p>
            <p>General Response: {record.general_response}</p>
            <p>Submission Url: {record.submission_url}</p>
            </div>"""
        self.send_email(
            self,
            mentor_email,
            "Notification: Approved Project Grading Result",
            "Notification: Approved Project Grading Result",
            email_body,
            "Notification: Approved Project Grading Result",
            record.submission_url,
            "Go to Project Submission",
        )

        return self.submit_grade()

    def button_disapprove(self):
        for record in self:
            record.lms_grade_update_status = "Idle"
            mentor_email = record.mentor_id.email
            email_body = f"""<div>
                <h2>Hello Admin,</h2>
                <h3 style="color: red;"><strong>Admin Disapproved Project Grading Result!</strong></h3>
                <p>Project: {record.project.title}</p>
                <p>Course name: {record.project.course.course_name}</p>
                <p>Course code: {record.project.course.course_code}</p>
                <p>Submission Note: {record.submission_note}</p>
                <p>General Response: {record.general_response}</p>
                <p>Submission Url: {record.submission_url}</p>
                </div>"""
            self.send_email(
                self,
                mentor_email,
                "Notification: Disapprove Project Grading Result",
                "Notification: Disapprove Project Grading Result",
                email_body,
                "Notification: Disapprove Project Grading Result",
                record.submission_url,
                "Go to Project Submission",
            )

            return {
                "type": "ir.actions.client",
                "tag": "soft_reload",
            }

    @api.depends("has_abnormal_result", "approved")
    def _compute_should_display_approve_btn(self):
        is_admin = self.env.su or self.env.user._is_admin()
        for r in self:
            r.should_display_approve_btn = (
                is_admin and r.has_abnormal_result and not r.approved
            )

    def write(self, values):
        if self.env.su or self.env.user.login == self.mentor_id.email:
            return super(ProjectSubmission, self).write(values)
        else:
            raise UserError(
                "This submission is already assigned to another mentor. You are not allowed to grade it."
            )
