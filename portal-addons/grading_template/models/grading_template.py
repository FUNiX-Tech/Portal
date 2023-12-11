# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.addons.website.tools import text_from_html
import html

UNIQUE_CODE = (
    "unique_grading_template_code",
    "unique(code)",
    "Grading template code must be unique.",
)

UNIQUE_NAME = (
    "unique_grading_template_name",
    "unique(name)",
    "Grading template name must be unique.",
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

    def button_apply_template(self):
        picked_template = self.env.context.get("picked_template")
        criterion_repsonse_id = self.env.context.get("criterion_response_id")
        criterion_repsonse = (
            self.env["project_criterion_response"]
            .sudo()
            .search([("id", "=", criterion_repsonse_id)])[0]
        )
        feedback_lead = picked_template

        feedback_body = "<ul>"

        for spec in criterion_repsonse.specifications:
            if text_from_html(spec.feedback).strip() != "":
                feedback_body += f"<li>{spec.feedback}</li>"

        feedback_body += "</ul>"

        criterion_repsonse.feedback = html.unescape(
            feedback_lead + feedback_body
        )

        return True
