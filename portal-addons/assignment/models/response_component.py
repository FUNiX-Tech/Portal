# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResponseComponent(models.Model):
    _name = "response_component"
    _description = "response_component"
    _rec_name = "name"

    # name, required, order
    TYPES = [
        ("Lead*", False, 1),
        ("Errors*", False, 2),
        ("Corrects*", False, 2),
        ("Suggestions", True, 3),
        ("Internal Documents/Videos", True, 4),
        ("Additional Reading", True, 5),
    ]

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    INCOMPLETE = ("incomplete", "Incomplete")
    DEFAULT_RESULT = NOT_GRADED[0]

    name = fields.Char("Name")
    content = fields.Html(string="Html Content", default="")
    criterion_response = fields.Many2one(
        "assignment_criterion_response", string="Criterion Response"
    )
    is_optional = fields.Boolean(string="Is Optional", default=True)
    number = fields.Integer(string="Order")
    is_show = fields.Boolean(
        string="Is Show", compute="_compute_is_show", store=True
    )
    criterion_response_result = fields.Selection(
        [NOT_GRADED, PASSED, DID_NOT_PASS, INCOMPLETE],
        string="Criterion Result",
        related="criterion_response.result",
        store=True,
    )

    @api.depends("criterion_response_result")
    def _compute_is_show(self):
        for record in self:
            if record.criterion_response_result == "passed":
                if record.name in ["Errors*", "Internal Documents/Videos"]:
                    record.is_show = False
                else:
                    record.is_show = True

            elif record.criterion_response_result in [
                "did_not_pass",
                "incomplete",
            ]:
                if record.name in ["Corrects*"]:
                    record.is_show = False
                else:
                    record.is_show = True
            else:
                record.is_show = False
