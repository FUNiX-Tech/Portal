# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_TITLE_PROJECT = (
    "unique_project_criterion_material_name_criterion",
    "unique(name, criterion)",
    "The titles of criteria Groups must be unique within a project.",
)


class ProjectCriterionMaterial(models.Model):
    _name = "project_criterion_material"
    _description = "project_criterion_material"
    _rec_name = "name"

    content = fields.Html("Content", required=True)

    name = fields.Char(string="Name")

    criterion = fields.Many2one(
        "project_criterion", string="Criterion", required=True
    )

    def button_insert_material(self):
        material = self.env.context.get("material")
        criterion_repsonse_id = self.env.context.get("criterion_response_id")
        criterion_repsonse = (
            self.env["project_criterion_response"]
            .sudo()
            .search([("id", "=", criterion_repsonse_id)])[0]
        )
        criterion_repsonse.feedback += material
        return True
