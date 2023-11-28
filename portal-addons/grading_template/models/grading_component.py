# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_CODE = (
    "unique_grading_component_code",
    "unique(code)",
    "Grading component code must be unique.",
)

UNIQUE_NAME = (
    "unique_grading_component_name",
    "unique(name)",
    "Grading component display name must be unique.",
)


class GradingComponent(models.Model):
    """
    content field examples:
    - ICON1 + Awesome

    - ICON2 + Required changes
        html template

    - ICON3 + template text + url
    """

    _name = "grading_component"
    _description = "grading_component"
    _rec_name = "name"

    categories = fields.Many2many(
        comodel_name="grading_component_category",
        relation="grading_compoennt_and_grading_component_category",
        column1="grading_component_ids",
        column2="grading_component_category_ids",
        string="Grading Component Categories",
    )
    content = fields.Html(string="Content", required=True)
    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)

    _sql_constraints = [UNIQUE_CODE, UNIQUE_NAME]

    def append_content(self):
        return True
