# -*- coding: utf-8 -*-

from odoo import models, fields

class Assignment(models.Model):
    _name = 'assignment'
    _description = 'assignment'

    name = fields.Char("Tên assignment", required=True)
    course_code = fields.Char("Mã môn học", required=True)
    order = fields.Integer(string="STT", required=True)