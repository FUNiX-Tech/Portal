# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IndividualCustomLearningPath(models.Model):
    _name = "individual_learning_path"
    _description = "Learning Path for individual student"

    name = fields.Char(
        string="Name",
        required=True,
    )

    description = fields.Html(
        string="Description",
    )
