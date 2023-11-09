from odoo import models, fields


class SubmissionHistory(models.Model):
    _name = "submission_history"
    _description = "Submission History"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    assignment_id = fields.Many2one("assignment", string="Assignment")
    submission_id = fields.Many2one(
        "assignment_submission", string="Submission"
    )
    created_at = fields.Datetime(
        string="Submission Time", default=fields.Datetime.now, required=True
    )
    status = fields.Selection(
        [
            ("not_submitted", "Not submitted"),
            ("submission_failed", "Submission failed"),
            ("submitted", "Submitted"),
            ("submission_cancelled", "Submission cancelled"),
            ("grading", "Grading"),
            ("graded", "Graded"),
        ],
        string="Status",
        default="not_submitted",
        required=True,
    )
