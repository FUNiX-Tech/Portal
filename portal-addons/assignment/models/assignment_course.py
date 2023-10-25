# -*- coding: utf-8 -*-

from odoo import models, fields

class AssignmentCourse(models.Model):
    _name = 'assignment_course'
    _description = 'assignment_course'
    _rec_name = 'code'

    code = fields.Char("Mã môn học", required=True)

    _sql_constraints = [ ('unique_course_code', 'UNIQUE(code)', 'Mã course là duy nhất.') ]