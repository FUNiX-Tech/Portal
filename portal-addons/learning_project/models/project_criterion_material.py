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
    name = fields.Char("Name")
    criterion = fields.Many2one(
        "project_criterion", string="Criterion", required=True
    )
