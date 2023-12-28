# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ..validators.validators import (
    check_fields_presence,
    check_has_course,
    check_student,
)


class CourseManagement(http.Controller):
    # API check course has enrolled yet or not?
    @http.route(
        "/api/course_management/check_enroll",
        type="http",
        auth="none",
        method=["GET"],
        cors="*",
    )
    @check_fields_presence("course_code", "student_email")
    @check_has_course("course_code")
    @check_student("student_email")
    def check_enroll(self, **kw):
        course_code = request.params.get("course_code").replace(
            " ", "+"
        )  # If in url query params contain "+" it will be replaced by " ". So that we need to revert it before proceeding
        student_email = request.params.get("student_email")
        course = (
            request.env["course_management"]
            .sudo()
            .search(
                [
                    ("course_code", "=", course_code),
                    ("student_ids.email", "in", [student_email]),
                ]
            )
        )
        if course:
            enrolled = True
        else:
            enrolled = False
        return http.request.make_json_response(
            data={"enrolled": enrolled}, status=200
        )

    # API link(enroll) course with student
    @http.route(
        "/api/course_management/enroll",
        type="http",
        auth="none",
        method=["POST"],
        csrf=False,
        cors="*",
    )
    @check_fields_presence("course_code", "student_email")
    @check_has_course("course_code")
    @check_student("student_email")
    def course_enroll(self, **kw):
        student_id = self.student.id
        self.course.write({"student_ids": [(4, student_id)]})
        return http.request.make_json_response(
            data={"message": "Enrolled successfully!"}, status=200
        )

    # API unlink (unenroll) course with student
    @http.route(
        "/api/course_management/unenroll",
        type="http",
        auth="none",
        method=["POST"],
        csrf=False,
        cors="*",
    )
    @check_fields_presence("course_code", "student_email")
    @check_has_course("course_code")
    @check_student("student_email")
    def course_unenroll(self, **kw):
        student_id = self.student.id
        self.course.student_ids = [(3, student_id)]
        return http.request.make_json_response(
            data={"message": "Unenrolled successfully!"}, status=200
        )
