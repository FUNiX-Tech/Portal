# -*- coding: utf-8 -*-
# from odoo import http


# class MentorManagement(http.Controller):
#     @http.route('/mentor_management/mentor_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mentor_management/mentor_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mentor_management.listing', {
#             'root': '/mentor_management/mentor_management',
#             'objects': http.request.env['mentor_management.mentor_management'].search([]),
#         })

#     @http.route('/mentor_management/mentor_management/objects/<model("mentor_management.mentor_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mentor_management.object', {
#             'object': obj
#         })

from odoo import http
from odoo.http import request


class MentorManagementAPI(http.Controller):
    @http.route(
        "/api/assignment/submission/<int:submission_id>",
        type="http",
        auth="none",
        methods=["GET"],
    )
    def get_submission_status(self, submission_id):
        submission = (
            request.env["assignment_submission"]
            .sudo()
            .search([("id", "=", submission_id)], limit=1)
        )
        if not submission:
            # return {'error': 'Submission not found'}
            return http.request.make_json_response(
                data={"error": "Submission not found"},
                status=404,
            )

        return http.request.make_json_response(
            data={
                "submission_id": submission.id,
                "student": submission.student.name,
                "assignment": submission.assignment.title,
                "submission_url": submission.submission_url,
                "result": "submission.result",
                "has_graded_all_criteria": submission.has_graded_all_criteria,
                "course": submission.course,
            },
            status=200,
        )
