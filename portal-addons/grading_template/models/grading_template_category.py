# -*- coding: utf-8 -*-
from odoo import models, fields

UNIQUE_CODE = (
    "unique_grading_template_category_code",
    "unique(code)",
    "Grading template category code must be unique.",
)

UNIQUE_NAME = (
    "unique_grading_template_category_name",
    "unique(name)",
    "Grading template category name must be unique.",
)


class GradingTemplateCategory(models.Model):
    _name = "grading_template_category"
    _description = "grading_template_category"
    _rec_name = "name"

    code = fields.Char(string="Code", required=True)

    name = fields.Char(string="Display Name", required=True)

    templates = fields.One2many(
        comodel_name="grading_template",
        inverse_name="category",
        string="Grading Templates",
    )

    _sql_constraints = [UNIQUE_CODE, UNIQUE_NAME]
