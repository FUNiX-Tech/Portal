# -*- coding: utf-8 -*-

from odoo import models, fields

class AssignmentSubmission(models.Model):
    _name = 'assignment_submission'
    _description = 'assignment_submission'

    student = fields.Many2one('portal_student_management.portal.student', string="Học viên") 
    assignment = fields.Many2one("assignment", string="Assignment")
    submission_url = fields.Char(string="Submission Url") 