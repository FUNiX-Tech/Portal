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
        if all(
            key in list(data.keys())
            for key in [
                "student_email",
                "ticket_category",
                "course_id",
            ]
        ):
            student_email = data.get("student_email")
            student = (
                request.env["portal.student"]
                .sudo()
                .search([("email", "=", student_email)])
            )
            course_code = data.get(
                "course_id"
            )  # code_id from lms is course_code in portal
            course = (
                request.env["course_management"]
                .sudo()
                .search([("course_code", "=", course_code)])
            )

            if student and course:
                request.env["feedback_ticket"].sudo().create(
                    {
                        "ticket_category": data.get("ticket_category"),
                        "course_rel": course.id,
                        "lesson_url": data.get("lesson_url"),
                        "ticket_description": data.get("ticket_description"),
                        "ticket_requester": student.id,
                        "ticket_attachment": data.get("image"),
                    }
                )
                return http.request.make_json_response(
                    data={"message": "Your ticket has been generated!"},
                    status=200,
                )
            else:
                return http.request.make_json_response(
                    data={
                        "message": "Student email or Course id do not found!"
                    },
                    status=400,
                )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure 'student_email', 'ticket_category' and 'course_id' are included in body request"
                },
                status=400,
            )
