# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
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
    feed_back = fields.Html(string="Feedback")
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

    previously_passed = fields.Boolean(
        string="Previously Passed", compute="_compute_previously_passed"
    )
    previously_feedback = fields.Html(
        string="Previously Feedback", compute="_compute_previously_feedback"
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

    @api.depends("submission")
    def _compute_previously_passed(self):
        for record in self:
            project = record.submission.project

            submissions = project.submissions.sorted(key=lambda item: item.id)

            nearest_submission = None
            for submission in submissions:
                if (
                    submission.result
                    not in ["submission_canceled", "not_graded"]
                    and record.submission.id != submission.id
                ):
                    nearest_submission = submission
                    break

            if nearest_submission is None:
                record.previously_passed = False
                return

            previously_response = list(
                filter(
                    lambda response: response.criterion.id
                    == record.criterion.id,
                    nearest_submission.criteria_responses,
                )
            )[0]
            record.previously_passed = previously_response.result == "passed"

    @api.depends("submission")
    def _compute_previously_feedback(self):
        nearest_response = self._get_nearest_respone()

        for record in self:
            record.previously_feedback = (
                "" if nearest_response is None else nearest_response.feed_back
            )

    def _get_nearest_respone(self):
        for record in self:
            project = record.submission.project

            submissions = project.submissions.sorted(key=lambda item: item.id)

            nearest_submission = None
            for submission in submissions:
                if (
                    submission.result
                    not in ["submission_canceled", "not_graded"]
                    and record.submission.id != submission.id
                ):
                    nearest_submission = submission
                    break

            if nearest_submission is None:
                return None

            nearest_response = list(
                filter(
                    lambda response: response.criterion.id
                    == record.criterion.id,
                    nearest_submission.criteria_responses,
                )
            )[0]
            return nearest_response
