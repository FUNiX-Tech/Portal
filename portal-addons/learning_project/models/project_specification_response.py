# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from ..common import PASSED, DID_NOT_PASS, INCOMPLETE, NOT_GRADED


class ProjectSpecificationResponse(models.Model):
    _name = "project_specification_response"
    _description = "project_specification_response"

    feedback = fields.Html(string="Feedback", default="")

    criterion_response = fields.Many2one(
        "project_criterion_response", string="Criterion Response"
    )

    specification = fields.Many2one(
        "project_specification", string="Specification"
    )

    specification_content = fields.Html(
        string="Specification Content", related="specification.content"
    )

    result = fields.Selection(
        [PASSED, DID_NOT_PASS, INCOMPLETE, NOT_GRADED],
        default=NOT_GRADED[0],
        string="Result",
    )

    _sql_constraints = [
        (
            "unique_criterion_response_and_specification",
            "unique(criterion_response, specification)",
            "Unique criterion response and specification",
        )
    ]

    def write(self, values):
        if (
            self.env.su
            or self.env.user.login
            == self.criterion_response.submission.mentor_id.email
        ):
            return super(ProjectSpecificationResponse, self).write(values)
        else:
            raise UserError(
                "This submission is already assigned to another mentor. You are not allowed to grade it."
            )
