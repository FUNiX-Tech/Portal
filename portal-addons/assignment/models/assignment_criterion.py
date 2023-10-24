# -*- coding: utf-8 -*-

from odoo import models, fields

class AssignmentCriterion(models.Model):
    _name = 'assignment_criterion'
    _description = 'assignment_criterion'

    name = fields.Char("Tên tiêu chí", required=True)
    specifications = fields.Html(string="Các yêu cầu", required=True)
    order = fields.Integer(string="STT", required=True)
    group = fields.Many2one("assignment_criterion_group", string="Nhóm tiêu chí", required=True)