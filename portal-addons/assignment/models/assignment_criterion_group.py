# -*- coding: utf-8 -*-

from odoo import models, fields

class AssignmentCriterionGroup(models.Model):
    _name = 'assignment_criterion_group'
    _description = 'assignment_criterion_group'

    name = fields.Char("Tên nhóm tiêu chí", required=True)
    order = fields.Integer(string="STT", required=True)
    assignment = fields.Many2one("assignment", string="Assignment", required=True)
