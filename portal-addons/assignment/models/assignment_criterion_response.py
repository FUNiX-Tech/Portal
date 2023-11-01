# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AssignmentCriterionResponse(models.Model):
    _name = 'assignment_criterion_response'
    _description = 'assignment_criterion_response'
    _rec_name = "criterion"

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    DEFAULT_RESULT = NOT_GRADED[0]

    submission = fields.Many2one("assignment_submission", required=True, readonly=True)
    criterion = fields.Many2one("assignment_criterion", required=True, readonly=True)
    feed_back = fields.Html(string="Nhận xét", default="")
    result = fields.Selection([ NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW ], required=True, string="Kết quả", default=DEFAULT_RESULT)
    number = fields.Integer(related='criterion.number')

    _sql_constraints = [ ('unique_submission_criterion', 'unique(submission, criterion', 'Mỗi submission chỉ được chấm 1 lần.') ]

    @api.constrains('submission')
    def _check_the_same_assignment(self):
        for record in self:
            if record.criterion.assignment.id != record.submission.assignment.id:
                raise ValidationError("Criterion and submission must be belong to an assignment")
            
    @api.constrains('criterion')
    def _check_the_same_assignment(self):
        for record in self:
            if record.criterion.assignment.id != record.submission.assignment.id:
                raise ValidationError("Criterion and submission must be belong to an assignment")
            