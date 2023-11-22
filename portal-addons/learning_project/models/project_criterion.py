# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_PROJECT_CRITERION_NAME = (
    "unique_project_criterion_name",
    "unique(title, project)",
    "The criteria in an project must not have the same names.",
)
UNIQUE_PROJECT_CRITERION_ORDER = (
    "unique_project_criterion_order",
    "unique(number, project)",
    "Criterion numbers conflict.",
)


class ProjectCriterion(models.Model):
    _name = "project_criterion"
    _description = "project_criterion"
    _rec_name = "title"

    title = fields.Char("Criterion name", required=True)
    specifications = fields.Html(string="Specifications", required=True)
    number = fields.Integer(string="Number", required=True)
    project = fields.Many2one("project", required=True)

    _sql_constraints = [
        UNIQUE_PROJECT_CRITERION_NAME,
        UNIQUE_PROJECT_CRITERION_ORDER,
    ]
