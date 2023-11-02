# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import base64


class FeedbackTicket(http.Controller):
    # API to create ticket
    @http.route(
        "/api/feedback-ticket-management/create",
        type="http",
        auth="public",
        method=["POST"],
        csrf=False,
    )
    def create_ticket(self, **kw):
        data = http.request.httprequest.form.to_dict(flat=True)
        image = http.request.httprequest.files.to_dict(flat=True)
        if image.get("image"):
            ticket_attachment = base64.b64encode(image["image"].read())
        else:
            ticket_attachment = None
        if all(
            key in list(data.keys())
            for key in ["ticket_title", "student_id", "ticket_category"]
        ):
            request.env["feedback_ticket"].sudo().create(
                {
                    "ticket_category": data.get("ticket_category"),
                    "ticket_title": data.get("ticket_title"),
                    "ticket_description": data.get("ticket_description"),
                    "ticket_requester": data.get("student_id"),
                    "ticket_attachment": ticket_attachment,
                }
            )
            return http.request.make_json_response(
                data={"message": "Your ticket has generated!"}, status=200
            )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure your request header type is form-data and 'ticket_title','student_id','ticket_category' are included"
                },
                status=400,
            )
