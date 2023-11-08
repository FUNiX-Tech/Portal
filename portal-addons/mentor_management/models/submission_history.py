from odoo import models, fields


class SubmissionHistory(models.Model):
    _name = "submission_history"
    _description = "Submission History"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    assignment_id = fields.Many2one(
        "assignment", string="Assignment", required=True
    )
    timestamp = fields.Datetime(
        string="Submission Time", default=fields.Datetime.now, required=True
    )
    status = fields.Selection(
        [
            ("not_submitted", "Chưa nộp"),
            ("submission_failed", "Nộp không thành công"),
            ("submitted", "Nộp thành công"),
            ("submission_cancelled", "Hủy nộp"),
            ("grading", "Đang chấm"),
            ("graded", "Đã có kết quả"),
        ],
        string="Status",
        default="not_submitted",
        required=True,
    )
