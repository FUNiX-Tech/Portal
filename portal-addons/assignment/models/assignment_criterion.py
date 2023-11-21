# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_ASSIGNMENT_CRITERION_NAME = (
    "unique_assignment_criterion_name",
    "unique(title, assignment)",
    "The criteria in an assignment must not have the same names.",
)
UNIQUE_ASSIGNMENT_CRITERION_ORDER = (
    "unique_assignment_criterion_order",
    "unique(number, assignment)",
    "Criterion numbers conflict.",
)

UNIQUE_TITLE_GROUP = (
    "unique_assignment_criterion_title_criteria_group",
    "unique(title, criteria_group)",
    "Conflict group - title.",
)

UNIQUE_NUMBER_GROUP = (
    "unique_assignment_criterion_number_criteria_group",
    "unique(number, criteria_group)",
    "Conflict group - number.",
)


class AssignmentCriterion(models.Model):
    _name = "assignment_criterion"
    _description = "assignment_criterion"
    _rec_name = "title"

    title = fields.Char("Criterion name", required=True)
    specifications = fields.Html(string="Specifications", required=True)
    number = fields.Integer(string="Number", required=True)
    assignment = fields.Many2one(
        "assignment", required=True, ondelete="cascade"
    )
    criteria_group = fields.Many2one(
        "learning_project_criteria_group", required=True, ondelete="cascade"
    )

    _sql_constraints = [
        UNIQUE_ASSIGNMENT_CRITERION_NAME,
        UNIQUE_ASSIGNMENT_CRITERION_ORDER,
        UNIQUE_TITLE_GROUP,
        UNIQUE_NUMBER_GROUP,
    ]
