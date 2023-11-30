# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectCriterionMaterial(models.Model):
    _name = "project_criterion_material"
    _description = "project_criterion_material"
    _rec_name = "content"

    content = fields.Html("Content", required=True)
    criterion = fields.Many2one(
        "project_criterion", string="Criterion", required=True
    )
