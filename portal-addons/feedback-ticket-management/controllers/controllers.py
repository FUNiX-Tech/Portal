# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class FeedbackTicket(http.Controller):
    # API to create ticket
    @http.route(
        "/api/feedback-ticket-management/create",
        type="http",
        auth="public",
        method=["POST"],
        csrf=False,
        cors="*",
    )
    def create_ticket(self, **kw):
        data = json.loads(http.request.httprequest.data.decode("utf-8"))
        print("asd", data)
        if all(
            key in list(data.keys())
            for key in [
                "ticket_title",
                "student_id",
                "ticket_category",
                "course_id",
                "lesson_url",
            ]
        ):
            request.env["feedback_ticket"].sudo().create(
                {
                    "ticket_category": data.get("ticket_category"),
                    "ticket_title": data.get("ticket_title"),
                    "course_rel": data.get("course_id"),
                    "lesson_url": data.get("lesson_url"),
                    "ticket_description": data.get("ticket_description"),
                    "ticket_requester": data.get("student_id"),
                    "ticket_attachment": data.get("image"),
                }
            )
            return http.request.make_json_response(
                data={"message": "Your ticket has been generated!"}, status=200
            )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure your request header type is form-data and 'ticket_title', 'student_id', 'ticket_category', 'lesson_url', 'course_id' are included"
                },
                status=400,
            )
