# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OrgCustomLearningPath(models.Model):
    _name = "organization_learning_path"
    _description = "Learning Path for organization"

    name = fields.Char(
        string="Name",
        required=True,
    )

    description = fields.Html(
        string="Description",
    )
