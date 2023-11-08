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

    # Lấy thông tin của một submission
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

    # Lấy danh sách các submissions theo course id
    @http.route("/api/assignment", type="http", auth="none", methods=["GET"])
    def get_submissions(self, **kw):
        # Lấy giá trị từ query string. Ví dụ: /api/submissions/?course_id=1
        course_id = kw.get("course_id")

        # Kiểm tra xem course_id có được cung cấp hay không và là một số
        if not course_id or not course_id.isdigit():
            return {"error": "Invalid course_id"}

        # Chuyển course_id thành số nguyên để sử dụng trong tìm kiếm
        course_id = int(course_id)

        # Kiểm tra xem course có tồn tại hay không
        course = (
            request.env["course_management"]
            .sudo()
            .search([("id", "=", course_id)], limit=1)
        )
        if not course:
            return http.request.make_json_response(
                data={"error": "Course not found"},
                status=404,
            )

        # Thực hiện tìm kiếm các submissions cho khóa học đó
        submissions = (
            request.env["assignment_submission"]
            .sudo()
            .search_read(
                [("assignment.course", "=", course_id)],
                fields=[
                    "student",
                    "assignment",
                    "submission_url",
                    "result",
                    "course",
                ],
            )
        )

        # Trả về kết quả
        # return {'submissions': submissions}
        return http.request.make_json_response(
            data=submissions,
            status=200,
        )
