# -*- coding: utf-8 -*-
from odoo import models, fields


class ProjectSpecification(models.Model):
    _name = "project_specification"
    _description = "project_specification"

    criterion = fields.Many2one("project_criterion", string="Criterion")

    content = fields.Html(string="Content", default="")
