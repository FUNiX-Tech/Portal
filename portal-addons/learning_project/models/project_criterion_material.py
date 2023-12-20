# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

UNIQUE_LABEL_CRITERION = (
    "unique_criterion_material_label",
    "unique(label, criterion)",
    "Unique material label in a criterion.",
)

UNIQUE_URL_CRITERION = (
    "unique_criterion_material_url",
    "unique(url, criterion)",
    "Unique material url in a criterion.",
)


class ProjectCriterionMaterial(models.Model):
    _name = "project_criterion_material"
    _description = "project_criterion_material"
    _rec_name = "label"

    label = fields.Char(string="Label", required=True)

    url = fields.Char(string="URL", required=True)

    append = fields.Html(string="Content To Append")

    auto_append = fields.Boolean(
        string="Will be automatically appended", default=False
    )

    criterion = fields.Many2one(
        "project_criterion", string="Criterion", required=True
    )

    _sql_constraints = [UNIQUE_LABEL_CRITERION, UNIQUE_URL_CRITERION]

    @api.constrains("auto_append")
    def _check_unique_auto_append(self):
        for r in self:
            if (
                r.auto_append is True
                and self.search_count(
                    [
                        ("auto_append", "=", True),
                        ("criterion", "=", r.criterion.id),
                    ]
                )
                > 1
            ):
                raise ValidationError(
                    "Auto append additional reading for this criterion already exists."
                )

    def button_use_additional_reading(self):
        criterion_response_id = self.env.context.get("criterion_response_id")
        print(criterion_response_id)
        criterion_response = self.env["project_criterion_response"].search(
            [("id", "=", criterion_response_id)]
        )
        for r in self:
            criterion_response.additional_reading = r.append

        return True
