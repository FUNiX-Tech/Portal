# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json
from ..utils.utils import json_response
from ..validators.validators import (
    check_fields_presence,
    check_url,
    check_ticket_category,
    check_has_course,
    check_student,
)

logger = logging.getLogger(__name__)


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
    @check_fields_presence(
        "student_email",
        "ticket_category",
        "course_id",
    )
    @check_ticket_category("ticket_category")
    @check_student("student_email")
    @check_has_course("course_id")
    @check_url("image", "lesson_url")
    def create_ticket(self, **kw):
        data = json.loads(http.request.httprequest.data.decode("utf-8"))
        student = self.student
        course = self.course

        if student and course:
            try:
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
                return json_response(
                    status=200,
                    data={"message": "Your ticket has been generated!"},
                )
            except Exception as e:
                logger.error(str(e))
                # end create submission history
                return json_response(500, {"message": "Internal Server Error"})
