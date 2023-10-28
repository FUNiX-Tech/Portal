# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_ASSIGNMENT_CRITERION_NAME = ('unique_assignment_criterion_name', 'unique(title, criterion_group)', 'Tên tiêu chí trong một nhóm tiêu chí không được giống nhau.') 
UNIQUE_ASSIGNMENT_CRITERION_ORDER = ('unique_assignment_criterion_order', 'unique(number, criterion_group)', 'Số thứ tự của tiêu chí trong một nhóm tiêu chí không được giống nhau.') 


class AssignmentCriterion(models.Model):
    _name = 'assignment_criterion'
    _description = 'assignment_criterion'
    _rec_name = 'title'

    title = fields.Char("Tên tiêu chí", required=True)
    specifications = fields.Html(string="Các yêu cầu", required=True)
    number = fields.Integer(string="STT", required=True)
    criterion_group = fields.Many2one("assignment_criterion_group", string="Nhóm tiêu chí", required=True)

    _sql_constraints = [ UNIQUE_ASSIGNMENT_CRITERION_NAME, UNIQUE_ASSIGNMENT_CRITERION_ORDER ]