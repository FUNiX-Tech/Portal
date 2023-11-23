# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from .response_component import ResponseComponent
from odoo.addons.website.tools import text_from_html


class ProjectCriterionResponse(models.Model):
    _name = "project_criterion_response"
    _description = "project_criterion_response"
    _rec_name = "criterion"

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    INCOMPLETE = ("incomplete", "Incomplete")
    DEFAULT_RESULT = NOT_GRADED[0]

    submission = fields.Many2one(
        "project_submission", required=True, readonly=True
    )
    criterion = fields.Many2one(
        "project_criterion", required=True, readonly=True
    )
    feed_back = fields.Html(string="Feedback", compute="_compute_feedback")
    feedback_components = fields.One2many(
        "response_component",
        inverse_name="criterion_response",
        string="Feedback Components",
    )
    result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, INCOMPLETE],
        required=True,
        string="Result",
        default=DEFAULT_RESULT,
    )
    number = fields.Integer(related="criterion.number")
    submission_result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW],
        related="submission.result",
    )
    criteria_group = fields.Many2one(
        related="criterion.criteria_group", store=True
    )  # store=True để có thể sort
    is_missing_required_feedback = fields.Boolean(
        compute="_check_missing_required_feedback", store=True
    )

    _sql_constraints = [
        (
            "unique_submission_criterion",
            "unique(submission, criterion)",
            "Duplicated criteria in a submission.",
        )
    ]

    @api.constrains("submission", "criterion")
    def _check_the_same_project(self):
        for record in self:
            if record.criterion.project.id != record.submission.project.id:
                raise ValidationError(
                    "Criterion and submission must belong to an project"
                )

    @api.model
    def create(self, vals):
        types = ResponseComponent.TYPES

        for type in types:
            component = self.env["response_component"].create(
                {
                    "name": type[0],
                    "is_optional": type[1],
                    "number": type[2],
                }
            )
            vals.setdefault("feedback_components", []).append(component.id)

        return super(ProjectCriterionResponse, self).create(vals)

    @api.depends("feedback_components", "result")
    def _compute_feedback(self):
        for record in self:
            html = ""
            for component in record.feedback_components:
                if component.is_show:
                    html += component.content

            record.feed_back = html

    @api.depends("feedback_components.content", "result", "feed_back")
    def _check_missing_required_feedback(self):
        for record in self:
            is_missing = False
            for component in record.feedback_components:
                if (
                    component.is_show
                    and not component.is_optional
                    and text_from_html(component.content).strip() == ""
                ):
                    is_missing = True
                    break

            record.is_missing_required_feedback = is_missing
