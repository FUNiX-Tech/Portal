# -*- coding: utf-8 -*-

from odoo import models, fields

UNIQUE_ASSIGNMENT_NAME = ('unique_assignment_name', 'unique(title, course)', 'Tên các assignment trong một course không được trùng nhau.') 
UNIQUE_ASSIGNMENT_ORDER = ('unique_assignment_order', 'unique(number, course)', 'Số thứ tự của assignment trong một course không được trùng nhau.') 

class Assignment(models.Model):
    _name = 'assignment'
    _description = 'assignment'
    _rec_name = "title"

    title = fields.Char("Tên assignment", required=True)
    course = fields.Many2one("course_management", string="Môn học", required=True) 
    number = fields.Integer(string="STT", required=True)

    _sql_constraints = [ UNIQUE_ASSIGNMENT_NAME, UNIQUE_ASSIGNMENT_ORDER ]