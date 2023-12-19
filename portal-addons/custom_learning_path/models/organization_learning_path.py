# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OrgCustomLearningPath(models.Model):
    _name = "organization_learning_path"
    _description = "Learning Path for organization"

    name = fields.Char(
        string="Name",
        required=True,
    )
    is_active = fields.Boolean(
        string="Is Active",
        default=True,
    )

    description = fields.Html(
        string="Description",
    )
