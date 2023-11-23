# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResponseComponent(models.Model):
    _name = "response_component"
    _description = "response_component"
    _rec_name = "name"

    # name, is_optional, order
    TYPES = [
        ("General*", False, 0),  # Nhận xét chung
        ("Errors*", False, 1),  # Đang sai như thế nào
        ("Annotations*", False, 2),  # Đang sai ở chỗ nào
        ("Suggestions*", False, 3),  # Gợi ý chỉnh sửa
        (
            "Internal Documents/Videos",
            True,
            4,
        ),  # Gợi ý xem lại bài học, video nào để chỉnh sửa
        ("Additional Reading", True, 5),  # Tài liệu đọc thêm
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
        "project_criterion_response", string="Criterion Response"
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
                record.is_show = record.name in [
                    "General*",
                    "Additional Reading",
                ]

            elif record.criterion_response_result == "did_not_pass":
                record.is_show = True

            elif record.criterion_response_result == "incomplete":
                record.is_show = record.name in [
                    "General*",
                    "Internal Documents/Videos",
                ]
            else:
                record.is_show = False
