# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_ASSIGNMENT_CRITERION_GROUP_NAME = ('unique_assignment_criterion_group_name', 'unique(title, assignment)', 'Tên nhóm tiêu chí trong một assignment không được giống nhau.') 
UNIQUE_ASSIGNMENT_CRITERION_GROUP_ORDER = ('unique_assignment_criterion_group_order', 'unique(number, assignment)', 'Số thứ tự của tiêu chí trong một assignment không được giống nhau.') 

class AssignmentCriterionGroup(models.Model):
    _name = 'assignment_criterion_group'
    _description = 'assignment_criterion_group'
    _rec_name = 'title'

    title = fields.Char("Tên nhóm tiêu chí", required=True)
    number = fields.Integer(string="STT", required=True)
    assignment = fields.Many2one("assignment", string="Assignment", required=True)

    _sql_constraints = [ UNIQUE_ASSIGNMENT_CRITERION_GROUP_NAME, UNIQUE_ASSIGNMENT_CRITERION_GROUP_ORDER ]
