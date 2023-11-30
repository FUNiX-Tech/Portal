# -*- coding: utf-8 -*-

from odoo import models, fields


UNIQUE_CODE = (
    "unique_grading_template_category_code",
    "unique(code)",
    "Grading component category code must be unique.",
)

UNIQUE_NAME = (
    "unique_grading_template_category_name",
    "unique(name)",
    "Grading component category display name must be unique.",
)


class GradingTemplateCategory(models.Model):
    _name = "grading_template_category"
    _description = "grading_template_category"
    _rec_name = "name"

    code = fields.Char("Code", required=True)
    name = fields.Char("Display Name", required=True)
    templates = fields.Many2many(
        comodel_name="grading_template",
        relation="grading_template_category_and_template",
        column1="grading_template_category_ids",
        column2="grading_template_ids",
        string="Grading Templates",
    )

    _sql_constraints = [UNIQUE_CODE, UNIQUE_NAME]
