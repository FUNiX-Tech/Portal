# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ...learning_project.utils.utils import json_response


class GradingTemplate(http.Controller):
    @http.route(
        "/api/v1/grading_template/templates/<string:code>",
        type="http",
        auth="public",
        methods=["GET"],
        cors="*",
        csrf=False,
    )
    def get_templates(self, code):
        templates = (
            request.env["grading_template"]
            .sudo()
            .search([("category.code", "=", code)])
        ).sorted("id")

        serialized = []
        for template in templates:
            serialized.append(
                {
                    "id": template.id,
                    "category": template.category.name,
                    "code": template.code,
                    "name": template.name,
                    "content": template.content,
                }
            )

        return json_response(200, "Success", serialized)
