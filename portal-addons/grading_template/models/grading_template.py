# -*- coding: utf-8 -*-

from odoo import models, fields, api

UNIQUE_CODE = (
    "unique_grading_template_code",
    "unique(code)",
    "Grading component code must be unique.",
)

UNIQUE_NAME = (
    "unique_grading_template_name",
    "unique(name)",
    "Grading component display name must be unique.",
)


class GradingTemplate(models.Model):
    _name = "grading_template"
    _description = "grading_template"
    _rec_name = "name"

    category = fields.Many2one(
        comodel_name="grading_template_category",
        string="Grading Template Category",
        required=True,
    )

    code = fields.Char("Code", required=True)
    name = fields.Char("Display Name", required=True)
    content = fields.Html(string="Content")
    components = fields.One2many(
        "grading_component", compute="_compute_components"
    )

    @api.depends("code")
    def _compute_components(self):
        for record in self:
            record.components = self.env["grading_component"].search([])

    def append_content(self):
        return True
