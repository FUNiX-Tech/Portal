# -*- coding: utf-8 -*-

from odoo import models, fields

class AssignmentSubmission(models.Model):
    _name = 'assignment_submission'
    _description = 'assignment_submission'

    student = fields.Many2one('portal.student', string="Học viên", readonly=True) 
    assignment = fields.Many2one("assignment", string="Assignment", readonly=True) 
    submission_url = fields.Char(string="Submission Url", readonly=True) 
    criteria_responses = fields.One2many("assignment_criterion_response", inverse_name="submission", string="Các tiêu chí") 