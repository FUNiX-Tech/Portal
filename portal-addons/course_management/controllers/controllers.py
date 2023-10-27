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
        if course_id and student_id:
            print("datacan:", course_id, student_id)
            course = (
                request.env["course_management"]
                .sudo()
                .search([("id", "=", course_id), ("student_ids", "in", [student_id])])
            )
            if course:
                enrolled = True
            else:
                enrolled = False
            return http.request.make_json_response(
                data={"enrolled": enrolled}, status=200
            )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure the URL include student_id and course_id as parameters"
                },
                status=400,
            )

    # API link(enroll) course with student
    @http.route(
        "/api/course_management/enroll",
        type="http",
        auth="none",
        method=["POST"],
        csrf=False,
    )
    def course_enroll(self, **kw):
        data = http.request.httprequest.data.decode("utf-8")
        data_parse = json.loads(data)
        if "course_id" in list(data_parse.keys()) and "student_id" in list(
            data_parse.keys()
        ):
            course_id = data_parse["course_id"]
            student_id = data_parse["student_id"]
            course = request.env["course_management"].sudo().browse(course_id)
            course.write({"student_ids": [(4, student_id)]})
            return http.request.make_json_response(
                data={"message": "Enrolled successfully!"}, status=200
            )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure the request body include key-value pairs of student_id and course_id"
                },
                status=400,
            )

    # API unlink (unenroll) course with student
    @http.route(
        "/api/course_management/unenroll",
        type="http",
        auth="none",
        method=["POST"],
        csrf=False,
    )
    def course_unenroll(self, **kw):
        data = http.request.httprequest.data.decode("utf-8")
        data_parse = json.loads(data)
        print(data_parse)
        if "course_id" in list(data_parse.keys()) and "student_id" in list(
            data_parse.keys()
        ):
            course_id = data_parse["course_id"]
            student_id = data_parse["student_id"]
            course = request.env["course_management"].sudo().browse(course_id)
            course.student_ids = [(3, student_id)]
            return http.request.make_json_response(
                data={"message": "Unenrolled successfully!"},
                status=200,
            )
        else:
            print("Asd")
            return http.request.make_json_response(
                data={
                    "message": "Please make sure the request body include key-value pairs of student_id and course_id"
                },
                status=400,
            )
