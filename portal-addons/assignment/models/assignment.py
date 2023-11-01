# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_ASSIGNMENT_NAME = (
    "unique_assignment_name",
    "unique(title, course)",
    "Duplicated assignment title.",
)
UNIQUE_ASSIGNMENT_ORDER = (
    "unique_assignment_order",
    "unique(number, course)",
    "Duplicated assignment numbers.",
)


class Assignment(models.Model):
    _name = "assignment"
    _description = "assignment"
    _rec_name = "title"

    title = fields.Char("Assignment name", required=True)
    course = fields.Many2one(
        "course_management", string="Course", required=True
    )
    number = fields.Integer(string="Number", required=True)
    criteria = fields.One2many(
        "assignment_criterion", inverse_name="assignment", string="Criteria"
    )

    _sql_constraints = [UNIQUE_ASSIGNMENT_NAME, UNIQUE_ASSIGNMENT_ORDER]
