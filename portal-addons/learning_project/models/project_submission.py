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
import html
from datetime import datetime
from ..common import (
    NOT_GRADED,
    CANCELED,
    PASSED,
    DID_NOT_PASS,
    UNABLE_TO_REVIEW,
    INCOMPLETE,
)

GRADE_STATUS = [
    ("idle", "Idle"),
    ("waiting_for_approving", "Waiting For Approving"),
    ("failed", "Failed"),
    ("success", "Success"),
]

# TODO: cho APPEND_ID về 1 nơi để dùng chung với wysiwyg.js
APPEND_ID = "94713822-9650-11ee-b9d1-0242ac120002"

MESSAGE_INFO_MENTOR = "This is an abnormal project grading result. An email was sent to admin. You'll get notification email when we're done with checking it."

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

    temp_result = fields.Char(
        string="Current Temp Result",
        compute="_compute_temp_result",
    )

    submission_note = fields.Text("Submission Note", readonly=True, default="")

    general_response = fields.Html(string="General Response", default="")

    has_graded_all_criteria = fields.Boolean(
        compute="_has_graded_all_criteria", store=True
    )

    course = fields.Char(related="project.course.course_name")

    grading_status = fields.Selection(
        GRADE_STATUS, string="Grading Status", default="idle"
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

    user_can_grade = fields.Boolean(
        string="Current user can grade this submission",
        compute="_compute_user_can_grade",
    )

    @api.depends(
        "criteria_responses.result",
        "criteria_responses.step",
        "general_response",
    )
    def _compute_temp_result(self):
        for record in self:
            # Assume all criteria have passed initially
            all_criteria_passed = True

            for response in record.criteria_responses:
                # Check if any criterion has not passed
                if response.result != PASSED[0]:
                    all_criteria_passed = False
                    break  # No need to check further if any criterion has not passed

            # Set temp_result based on whether all criteria have passed
            record.temp_result = (
                PASSED[1] if all_criteria_passed else DID_NOT_PASS[1]
            )

            return record.temp_result

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
        for record in self:
            is_unable_to_review = self.env.context.get("unable_to_review")

            # Chưa nhập nhận xét tổng thì không cho submit
            if text_from_html(record.general_response).strip() == "":
                raise UserError("Missing general response.")

            # Nếu không phải là unable to review, nếu chưa chấm hết các tiêu chí thì không cho submit
            if not record.has_graded_all_criteria and not is_unable_to_review:
                raise UserError("You haven't graded all criteria")

            # Nếu có kết quả chấm bất thường thì tạm ngưng, chờ admin approve
            if self._should_wait_for_approving(is_unable_to_review):
                record.grading_status = "waiting_for_approving"
                self._send_mail_admin_abnormal_result()
                return self.env["portal_dialog"].info("", MESSAGE_INFO_MENTOR)

            # Không có gì bất thường > đc coi là approved
            record.approved = True

            # Chốt kết quả
            record.result = self._calculate_result(is_unable_to_review)

            # Nếu project passed thì thêm additional reading vào các feedback tiêu chí
            if record.result == PASSED[0]:
                self._append_additional_reading()

            # Gửi email thông báo cho học viên
            # Tạo submission history
            mail_error = self._send_mail_student()
            create_history_error = self._create_submission_history()

            # Cập nhật điểm ở lms
            lms_error = self._push_grade_result_to_lms()

            # Hiển thị modal kết quả trên browser
            message = ProjectSubmission._compose_message(
                lms_error, mail_error, create_history_error
            )
            return self.env["portal_dialog"].info("", message)

    def _push_grade_result_to_lms(self):
        for record in self:
            # Dành cho local dev
            # nếu odoo config DEBUG_MODE == True và SKIP_PUSH_GRADE_TO_LMS == True thì bỏ qua bước này
            should_skip = (
                config.get("skip_push_grade_to_lms") is True
                and config.get("debug_mode") is True
            )
            if should_skip:
                logger.info(
                    "DEBUG MODE: skip PUSH GRADE TO LMS error because of debug_mode is True and skip_push_grade_to_lms is True"
                )
                return ""

            if record.result == UNABLE_TO_REVIEW[0]:
                return ""

            if record.result == NOT_GRADED[0]:
                return "The current submission result is not_graded. Result must be passed or did_not_pass."

            headers = {"Content-Type": "application/json"}
            payload = {
                "project_name": record.project.title,
                "course_code": record.project.course.course_code,
                "email": record.student.email,
                "result": record.result,
            }

            try:
                lms_base = self.env[
                    "service_key_configuration"
                ].get_api_key_by_service_name("LMS_BASE")

                if not lms_base:
                    record.grading_status = "failed"
                    return "Missing LMS_BASE"

                url = f"{lms_base}api/funix_portal/project/grade_project"

                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    logger.info("Pushed project grading result to LMS")
                    record.grading_status = "success"
                    return ""
                else:
                    record.grading_status = "failed"
                    logger.error(
                        f"Failed to push project grading result to LMS: {response.text}"
                    )

                    return f"ERROR:Failed to push project grading result to LMS: {response.text}"

            except Exception as e:
                record.grading_status = "failed"
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

        raise UserError(error_message)

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
            <h2>Hello Mentor,</h2>
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
            record.grading_status = "idle"
            mentor_email = record.mentor_id.email
            email_body = f"""<div>
                <h2>Hello Mentor,</h2>
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
        for r in self:
            if r.user_can_grade:
                return super(ProjectSubmission, self).write(values)
            else:
                raise UserError("You are not assigned to this submission.")

    def _append_additional_reading(self):
        """
        Thêm Additional Reading vào mỗi feedback tiêu chí của mentor
        """
        for r in self:
            for response in r.criteria_responses:
                if ProjectSubmission._already_has_additional_reading(
                    response.feedback
                ):
                    continue

                for material_item in response.criterion.material:
                    if material_item.auto_append is True:
                        feedback = html.unescape(
                            response.feedback + material_item.append
                        )
                        response.feedback = feedback

    def _send_mail_admin_abnormal_result(self):
        for r in self:
            admin_email = "vuntafx17889@funix.edu.vn"
            email_body = f"""<div>
                <h2>Hello Admin,</h2>
                <h3 style="color: red;"><strong>There is an abnormal grading result!</strong></h3>
                <p>Project: {r.project.title}</p>
                <p>Course name: {r.project.course.course_name}</p>
                <p>Course code: {r.project.course.course_code}</p>
                <p>Submission Note: {r.submission_note}</p>
                <p>General Response: {r.general_response}</p>
                <p>Submission Url: {r.submission_url}</p>
                </div>"""
            self.send_email(
                self,
                admin_email,
                "Notification: Abnormal Project Grading Result",
                "Notification: Abnormal Project Grading Result",
                email_body,
                "Notification: Abnormal Project Grading Result",
                r.submission_url,
                "Go to Project Submission",
            )

    def _send_mail_student(self):
        try:
            for record in self:
                email_body = self._create_student_email_body()
                self.send_email(
                    self,
                    record.student.email,
                    "Notification: Project Submission Results Available",
                    "Notification: Project Submission Results Available",
                    email_body,
                    "Notification: Project Submission Results Available",
                    record.submission_url,
                    "Go to Project Submission",
                )

                return ""
        except Exception as e:
            logger.error(str(e))
            return str(e)

    def _create_student_email_body(self):
        for record in self:
            if record.result == UNABLE_TO_REVIEW[0]:
                result = UNABLE_TO_REVIEW[1]
            elif record.result == DID_NOT_PASS[0]:
                result = DID_NOT_PASS[1]
            else:
                result = PASSED[1]

            email_body = f"""<div>
            <h2>Hello {record.student.name},</h2>
            <p>Project: {record.project.title}</p>
            <p>Course name: {record.project.course.course_name}</p>
            <p>Course code: {record.project.course.course_code}</p>
            <p>Result: {result}</p>
            <p>Submission Note: {record.submission_note}</p>
            <p>General Response: {record.general_response}</p>
            <p>Submission Url: {record.submission_url}</p>
            <strong>Thank you!</strong>
            </div>"""

            return email_body

    def _create_submission_history(self):
        try:
            for record in self:
                # create submission history --> graded status
                record.env["submission_history"].sudo().create(
                    {
                        "student_id": record.student.id,
                        "project_id": record.project.id,
                        "submission_id": record.id,
                        "status": "graded",  # Đặt trạng thái là 'graded'
                    }
                )
                return ""
        except Exception as e:
            logger.error(str(e))
            return str(e)

    def create_submission_history(self):
        submission = self
        if submission.result == CANCELED[0]:
            status = "submission_cancelled"

        if submission.result in [
            PASSED[0],
            DID_NOT_PASS[0],
            UNABLE_TO_REVIEW[0],
        ]:
            status = "graded"

        try:
            submission.env["submission_history"].sudo().create(
                {
                    "student_id": submission.student.id,
                    "project_id": submission.project.id,
                    "submission_id": submission.id,
                    "status": status,
                }
            )
        except Exception as e:
            logger.error(str(e))
            return str(e)

    def _calculate_result(self, is_unable_to_review):
        """
        Tính kết quả submission nếu không phải là unable to review và đã chấm hết các tiêu chí
        """

        if is_unable_to_review is True:
            return UNABLE_TO_REVIEW[0]

        for r in self:
            if any(
                response.result in [DID_NOT_PASS[0], INCOMPLETE[0]]
                for response in r.criteria_responses
            ):
                return DID_NOT_PASS[0]

            return PASSED[0]

    def _should_wait_for_approving(self, is_unable_to_review):
        if is_unable_to_review:
            return False

        for r in self:
            return r.has_abnormal_result and r.approved is False

    @classmethod
    def _compose_message(cls, lms_error, mail_error, create_history_error):
        message = ""

        if lms_error:
            message += lms_error
        else:
            message += "Successfully to push grade to lms. "

        if mail_error:
            message += f"Failed to send email to student: {mail_error}. "
        else:
            message += "Sent email to student. "

        if create_history_error:
            message += (
                f"Failed to create submission history: {create_history_error}"
            )

        return message

    @classmethod
    def _already_has_additional_reading(cls, feedback):
        try:
            feedback.index(APPEND_ID)
            return True
        except ValueError:
            return False

    def _compute_user_can_grade(self):
        for r in self:
            r.user_can_grade = (
                self.env.su
                or self.env.user.login == r.mentor_id.email
                or self.env.user.has_group(
                    "mentor_management.group_mentor_management_admin"
                )
            )

    def send_cancel_emails(self):
        """
        Gửi email thông báo cancel cho học viên và mentor
        """
        self._send_cancel_email_student()
        self._send_cancel_email_mentor()

    def _send_cancel_email_student(self):
        submission = self

        body = f"""<div>
        <h2>Hello {submission.student.name}</h2>
        <h3>You had successfully canceled Project Submission  </h3>
        <p>Project: {submission.project.title}</p>
        <p>Course name: {submission.project.course.course_name}</p>
        <p>Couse code: {submission.project.course.course_code}</p>
        <div>"""

        try:
            submission.send_email(
                submission,
                submission.student.email,
                "Notification: Project Submission Successfully Canceled",
                "Notification: Project Submission Successfully Canceled",
                body,
                "Project Submission Canceled Successfully",
                submission.submission_url,
                "Go to Project Submission",
            )
        except Exception as e:
            logger.error(str(e))

    def _send_cancel_email_mentor(self):
        submission = self

        body = f"""<div>
        <h2>Hello {submission.mentor_id.full_name}</h2>
        <h3>Your student {submission.student.email} had successfully canceled Project Submission</h3>
        <p>Project: {submission.project.title}</p>
        <p>Course name: {submission.project.course.course_name}</p>
        <p>Couse code: {submission.project.course.course_code}</p>
        <div>"""

        try:
            submission.send_email(
                submission,
                submission.mentor_id.email,
                "Notification: Your Student Canceled A Submission",
                "Notification: Your Student Canceled A Submission",
                body,
                "Your Student Canceled A Submission",
                submission.submission_url,
                "Go to Project Submission",
            )
        except Exception as e:
            logger.error(str(e))

    @property
    def cancel_error(self):
        submission = self

        if submission.result == CANCELED[0]:
            return "This submission has already canceled."

        if submission.result != NOT_GRADED[0]:
            return "You cannot cancel this submission because the submission has been graded."

        minutes = round(
            (datetime.now() - submission.create_date).total_seconds() / 60
        )

        if minutes > 30:
            return "You cannot cancel this submission because it was submitted more than 30 minutes ago."

        return ""
