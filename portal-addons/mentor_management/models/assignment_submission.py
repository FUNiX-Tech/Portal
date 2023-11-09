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
    )

    submission_id = fields.Char(
        string="Submission ID",
        required=True,
        copy=False,
        index=True,
        default=lambda self: _("New"),
    )

    @api.model
    def create(self, vals):
        if vals.get("submission_id", _("New")) == _("New"):
            vals["submission_id"] = self.env["ir.sequence"].next_by_code(
                "assignment.assignment_submission"
            ) or _("New")
        result = super(AssignmentSubmission, self).create(vals)
        return result

    def write(self, vals):
        # Gọi phương thức 'write' của lớp cơ sở trước để đảm bảo rằng mentor được cập nhật đúng cách.
        result = super(AssignmentSubmission, self).write(vals)

        # Kiểm tra xem 'mentor_id' có trong các giá trị được cập nhật không.
        if "mentor_id" in vals and vals["mentor_id"]:
            # Tạo một bản ghi mới trong SubmissionHistory với trạng thái 'grading'.
            self.env["submission_history"].sudo().create(
                {
                    "student_id": self.student.id,
                    "assignment_id": self.assignment.id,
                    "submission_id": self.id,  # Hoặc 'submission_id' nếu đó là trường liên kết bạn muốn sử dụng
                    "status": "grading",
                }
            )
        return result
