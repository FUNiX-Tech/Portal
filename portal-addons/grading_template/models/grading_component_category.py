# -*- coding: utf-8 -*-

from odoo import models, fields


UNIQUE_CODE = (
    "unique_grading_component_category_code",
    "unique(code)",
    "Grading component category code must be unique.",
)

UNIQUE_NAME = (
    "unique_grading_component_category_name",
    "unique(name)",
    "Grading component category name must be unique.",
)


class GradingComponentCategory(models.Model):
    _name = "grading_component_category"
    _description = "grading_component_category"
    _rec_name = "name"

    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    components = fields.Many2many(
        comodel_name="grading_component",
        relation="grading_compoennt_and_grading_component_category",
        column1="grading_component_category_ids",
        column2="grading_component_ids",
        string="Grading Components",
    )

    _sql_constraints = [UNIQUE_CODE, UNIQUE_NAME]
