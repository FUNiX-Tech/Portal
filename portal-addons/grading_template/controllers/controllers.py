# -*- coding: utf-8 -*-
import logging
import json
from odoo import http
from odoo.http import request
from datetime import datetime
from ...learning_project.utils.utils import json_response


class GradingTemplate(http.Controller):
    @http.route(
        "/api/v1/grading_template/components",
        type="http",
        auth="public",
        methods=["GET"],
        cors="*",
        csrf=False,
    )
    def get_components(self):
        components = (
            request.env["grading_component"].sudo().search([])
        ).sorted("id")

        serialized = []
        for component in components:
            serialized.append(
                {
                    "id": component.id,
                    "categories": list(
                        map(
                            lambda e: {
                                "id": e.id,
                                "name": e.name,
                                "code": e.code,
                            },
                            component.categories,
                        )
                    ),
                    "code": component.code,
                    "name": component.name,
                    "content": component.content,
                }
            )

        return json_response(200, "Success", serialized)

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
