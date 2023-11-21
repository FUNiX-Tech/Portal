# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_TITLE_PROJECT = (
    "unique_criteria_group_title",
    "unique(title, project)",
    "The titles of criteria Groups must be unique within a project.",
)
UNIQUE_NUMBER_PROJECT = (
    "unique_criteria_group_number",
    "unique(number, project)",
    "The numbers of criteria Groups must be unique within a project.",
)


class LearningProjectCriteriaGroup(models.Model):
    _name = "learning_project_criteria_group"
    _description = "learning_project_criteria_group"
    _rec_name = "title"

    title = fields.Char("Criteria Group Name", required=True)
    criteria = fields.One2many(
        "assignment_criterion",
        inverse_name="criteria_group",
        string="Criteria",
    )
    number = fields.Integer(string="Number", required=True)
    project = fields.Many2one("assignment", required=True, ondelete="cascade")

    _sql_constraints = [
        UNIQUE_TITLE_PROJECT,
        UNIQUE_NUMBER_PROJECT,
    ]
