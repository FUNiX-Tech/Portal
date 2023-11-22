# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_PROJECT_NAME = (
    "unique_project_name",
    "unique(title, course)",
    "Duplicated project title.",
)
UNIQUE_PROJECT_ORDER = (
    "unique_project_order",
    "unique(number, course)",
    "Duplicated project numbers.",
)


class Project(models.Model):
    _name = "project"
    _description = "project"
    _rec_name = "title"

    title = fields.Char("Project name", required=True)
    course = fields.Many2one(
        "course_management", string="Course", required=True
    )
    number = fields.Integer(string="Number", required=True)
    criteria = fields.One2many(
        "project_criterion", inverse_name="project", string="Criteria"
    )

    _sql_constraints = [UNIQUE_PROJECT_NAME, UNIQUE_PROJECT_ORDER]
