# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_ASSIGNMENT_CRITERION_NAME = ('unique_assignment_criterion_name', 'unique(title, assignment)', 'The criteria in an assignment must not have the same names.') 
UNIQUE_ASSIGNMENT_CRITERION_ORDER = ('unique_assignment_criterion_order', 'unique(number, assignment)', 'Criterion numbers conflict.') 


class AssignmentCriterion(models.Model):
    _name = 'assignment_criterion'
    _description = 'assignment_criterion'
    _rec_name = 'title'

    title = fields.Char("Tên tiêu chí", required=True)
    specifications = fields.Html(string="Các yêu cầu", required=True)
    number = fields.Integer(string="STT", required=True)
    assignment = fields.Many2one("assignment", required=True)

    _sql_constraints = [ UNIQUE_ASSIGNMENT_CRITERION_NAME, UNIQUE_ASSIGNMENT_CRITERION_ORDER ]