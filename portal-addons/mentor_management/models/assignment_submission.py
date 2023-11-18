# -*- coding: utf-8 -*-
"""
Need to set the following variables to config file:
- lms_submission_notification: the lms url to send submission result notification.
- email_from: sender email (e.g. notification@example.com)
"""


import logging

from odoo import _, api, fields, models
from odoo.tools import config

logger = logging.getLogger(__name__)


class AssignmentSubmission(models.Model):
    _inherit = "assignment_submission"
    _rec_name = "submission_id"

    mentor_id = fields.Many2one(
        "mentor_management",
        string="Mentor",
        # groups="mentor_management.group_mentor_management_admin",
        track_visibility=True,
    )

    submission_id = fields.Char(
        string="Submission ID",
        required=True,
        copy=False,
        index=True,
        default=lambda self: _("New"),
    )

    # Tạo 1 computed field để hiển thị email của student
    student_email = fields.Char(
        string="Student Email", compute="_compute_student_email"
    )

    # Tạo 1 computed field để hiển thị thời gian nộp bài
    submission_date = fields.Datetime(
        string="Submit time", compute="_compute_submission_date"
    )

    # Tạo 1 computed field để hiển thị status của submission liên kết với submission_history
    latest_submission_status = fields.Selection(
        [
            ("not_submitted", "Not submitted"),
            ("submission_failed", "Submission failed"),
            ("submitted", "Submitted"),
            ("submission_cancelled", "Submission cancelled"),
            ("grading", "Grading"),
            ("graded", "Graded"),
        ],
        string="Submission Status",
        compute="_compute_submission_status",
    )

    # Tạo 1 computed field để check xem user hiện tại có phải là mentor của submission này không
    mentor_user_id = fields.Many2one(
        "res.users", compute="_compute_mentor_user_id", store=True
    )

    can_submit = fields.Boolean(
        string="Can Submit",
        compute="_compute_can_submit",
    )

    @api.model
    def create(self, vals):
        if vals.get("submission_id", _("New")) == _("New"):
            vals["submission_id"] = self.env["ir.sequence"].next_by_code(
                "assignment.assignment_submission"
            ) or _("New")
        result = super(AssignmentSubmission, self).create(vals)
        return result

    # Tạo 1 computed field để hiển thị email của student
    @api.depends("student")
    def _compute_student_email(self):
        for record in self:
            record.student_email = record.student.email

    # Tạo 1 computed field để hiển thị thời gian nộp bài
    @api.depends("create_date")
    def _compute_submission_date(self):
        for record in self:
            record.submission_date = record.create_date

    # Tạo 1 computed field để hiển thị status của submission liên kết với submission_history
    def _compute_submission_status(self):
        # tìm status của submission liên kết với submission_history
        # status có created_at mới nhất
        # student_id, assignment_id, submission_id giống với submission hiện tại
        for record in self:
            submission_history = self.env["submission_history"].search(
                [
                    ("student_id", "=", record.student.id),
                    ("assignment_id", "=", record.assignment.id),
                    ("submission_id", "=", record.id),
                ],
                order="created_at desc",
                limit=1,
            )
            if submission_history:
                record.latest_submission_status = submission_history.status
            else:
                record.latest_submission_status = ""

    @api.depends("mentor_id")
    def _compute_mentor_user_id(self):
        for record in self:
            if record.mentor_id:
                # Tìm user có email giống với email của mentor
                user = self.env["res.users"].search(
                    [("login", "=", record.mentor_id.email)], limit=1
                )
                record.mentor_user_id = user.id
            else:
                record.mentor_user_id = False

    @api.depends("mentor_user_id")
    def _compute_can_submit(self):
        for record in self:
            print("record.mentor_user_id", record.mentor_user_id)
            print("self.env.user", self.env.user)

            # kiểm tra xem user đang đăng nhập có trùng với mentor_user_id không
            if record.mentor_user_id == self.env.user:
                record.can_submit = True
                print("record.can_submit", record.can_submit)
            else:
                record.can_submit = False
                print("record.can_submit", record.can_submit)

    def write(self, vals):
        # Gọi phương thức 'write' của lớp cơ sở trước để đảm bảo rằng mentor được cập nhật đúng cách.
        result = super(AssignmentSubmission, self).write(vals)

        # Kiểm tra xem 'mentor_id' có trong các giá trị được cập nhật không.
        if "mentor_id" in vals and vals["mentor_id"]:
            # Lấy mentor_id từ các giá trị được cập nhật
            mentor_id = vals["mentor_id"]
            # Tìm mentor có id giống với mentor_id
            mentor = self.env["mentor_management"].search(
                [("id", "=", mentor_id)], limit=1
            )

            # lấy thông tin về AssignmentSubmission như submission_url, course, assignment title, student email
            submission_url = self.submission_url
            print("submission_url", self.submission_url)
            print("vals[mentor_id]", vals["mentor_id"])
            course = self.assignment.course
            assignment_title = self.assignment.title
            student_email = self.student_email

            # Tạo nội dung email
            body = f"""<div>
            <h2>Hello {mentor.full_name}</h2>
            <h3>You have an Learning Project Submission to grade</h3>
            <p>Assignment: {assignment_title}</p>
            <p>Course name: {course.course_name}</p>
            <p>Couse code: {course.course_code}</p>
            <p>Student email: {student_email}</p>
            <p>I hope you happy with that</p>
            <strong>Thank you!</strong>
            <div>"""

            # Gửi email
            self.send_email(
                self,
                mentor.email,
                "Assignment Submission Notification",
                "Assignment Submission Notification",
                body,
                "Your description assign mentor to grade",
                submission_url,
                "Go to Learning Project Submission",  # Button text
            )

            # Tạo một bản ghi mới trong SubmissionHistory với trạng thái 'grading'.
            self.env["submission_history"].sudo().create(
                {
                    "student_id": self.student.id,
                    "assignment_id": self.assignment.id,
                    "submission_id": self.id,
                    "status": "grading",
                }
            )
        # nếu không có 'mentor_id' trong các giá trị được cập nhật
        # Tạo một bản ghi mới trong SubmissionHistory với trạng thái 'submitted'
        # --> khi reassign mentor về trống sẽ trả về trạng thái 'submitted'
        else:
            self.env["submission_history"].sudo().create(
                {
                    "student_id": self.student.id,
                    "assignment_id": self.assignment.id,
                    "submission_id": self.id,
                    "status": "submitted",
                }
            )
        return result
