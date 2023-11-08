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
