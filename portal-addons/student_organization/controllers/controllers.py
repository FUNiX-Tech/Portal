# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class StudentGroup(http.Controller):
    # API search organization by its name
    @http.route(
        "/api/student_organization/search_org",
        type="http",
        auth="none",
        method=["GET"],
        cors="*",
    )
    def search_org_by_name(self, **kw):
        """
        Search for an organization by its name.
        :param org_name: The name of the organization to search for.
        :type org_name: str
        :return: A JSON response containing information about the organization, such as its name, creator, note, students enrolled, courses enrolled, and creation date.
                If the organization is found, the response has a status code of 200.
                If the organization is not found, the response has a status code of 400 and a message indicating that the organization does not exist.
                If the org_name parameter is not provided in the URL, the response has a status code of 400 and a message indicating that the parameter is missing.
        """
        org_name = kw.get("org_name")
        if org_name:
            organization = (
                request.env["student_organization"]
                .sudo()
                .search([("name", "=", org_name)])
            )
            if organization:
                courses = organization.course_ids.mapped("course_code")
                students = organization.student_ids.mapped("email")
                return http.request.make_json_response(
                    data={
                        "name": organization.name,
                        "creator": organization.creator,
                        "note": organization.note or "",
                        "students_enrolled": students,
                        "courses_enrolled": courses,
                        "created_at": organization.created_at,
                    },
                    status=200,
                )
            else:
                return http.request.make_json_response(
                    data={"message": "Organization Was Not Found!"},
                    status=400,
                )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure the URL include org_name as parameters"
                },
                status=400,
            )

    # API add student to organization
    @http.route(
        "/api/student_organization/add_student",
        type="http",
        auth="none",
        method=["POST"],
        csrf=False,
        cors="*",
    )
    def add_student_to_group(self, **kw):
        data_body = http.request.httprequest.data.decode("utf-8")
        data_parse = json.loads(data_body)
        if all(
            key in list(data_parse.keys())
            for key in [
                "student",
                "organization",
            ]
        ):
            organization = data_parse["organization"]
            organization = (
                request.env["student_organization"]
                .sudo()
                .search([("name", "=", organization)])
            )
            if organization:
                students = data_parse["student"]
                fail_student = []  # student not found by email
                success_student = []  # student can search
                for email in students:
                    student = (
                        request.env["portal.student"]
                        .sudo()
                        .search([("email", "=", email)])
                    )
                    if not student:
                        fail_student.append(email)
                    else:
                        success_student.append(student.id)
                print(fail_student, success_student)
                if len(fail_student) == 0:
                    organization.write(
                        {
                            "student_ids": [  #
                                [
                                    6,
                                    False,
                                    list(
                                        set(success_student).union(
                                            set(organization.student_ids.ids)
                                        )
                                    ),
                                ]
                            ]
                        }
                    )
                    return http.request.make_json_response(
                        data={"message": "Student added successfully!"},
                        status=200,
                    )
                else:
                    return http.request.make_json_response(
                        data={
                            "message": f"{(', ').join(fail_student)} were not found!"
                        },
                        status=400,
                    )
            else:
                return http.request.make_json_response(
                    data={"message": "Organization Was Not Found!"},
                    status=400,
                )
        else:
            return http.request.make_json_response(
                data={
                    "message": "Please make sure the request body include key-value pairs of student and organization"
                },
                status=400,
            )
