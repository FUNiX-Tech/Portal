# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class CourseManagement(http.Controller):
    # API check course has enrolled yet or not?
    @http.route(
        "/api/course_management/check_enroll", type="http", auth="none", method=["GET"]
    )
    def check_enroll(self, **kw):
        course_id = kw.get("course_id")
        student_id = kw.get("student_id")
        print("datacan:", course_id, student_id)
        course = (
            request.env["course_management"]
            .sudo()
            .search([("id", "=", course_id), ("student_ids", "in", [student_id])])
        )
        if course:
            return http.request.make_json_response(data={"enrolled": True}, status=200)
        else:
            return http.request.make_json_response(data={"enrolled": False}, status=200)

    # API link(enroll) course with student
    @http.route(
        "/api/course_management/enroll", type="json", auth="none", method=["POST"]
    )
    def course_enroll(self, **kw):
        data = http.request.httprequest.data.decode("utf-8")
        data_parse = json.loads(data)
        course_id = data_parse["course_id"]
        student_id = data_parse["student_id"]
        course = request.env["course_management"].sudo().browse(course_id)
        course.write({"student_ids": [(4, student_id)]})
        return http.request.make_json_response(
            data={"message": "Enrolled successfully!"}, status=200
        )

    # API unlink (unenroll) course with student
    @http.route(
        "/api/course_management/unenroll", type="json", auth="none", method=["POST"]
    )
    def course_unenroll(self, **kw):
        data = http.request.httprequest.data.decode("utf-8")
        data_parse = json.loads(data)
        course_id = data_parse["course_id"]
        student_id = data_parse["student_id"]
        course = request.env["course_management"].sudo().browse(course_id)
        course.student_ids = [(3, student_id)]
        return http.request.make_json_response(
            data={"message": "Unenrolled successfully!"}, status=200
        )
