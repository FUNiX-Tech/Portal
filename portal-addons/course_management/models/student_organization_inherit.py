from odoo import models, fields, api
from odoo.exceptions import UserError
import requests


class StudentOrganization(models.Model):
    _inherit = "student_organization"
    course_ids = fields.Many2many(
        comodel_name="course_management",
        relation="courses_enroll_organizations",
        column1="organization_ids",
        column2="course_ids",
        string="Courses Enrolled",
    )

    @api.model
    def create(self, vals):
        """
        override create method, in case of create organization have list course and student at the same time,
        Logic will be handle to make students and course link each other
        """
        org = super(StudentOrganization, self).create(vals)
        course_ids = org.course_ids.ids
        student_ids = org.student_ids.ids
        if course_ids != [] and student_ids != []:
            for course in org.course_ids:
                course.write(
                    {
                        "student_ids": [
                            (4, student_id) for student_id in student_ids
                        ]
                    }
                )
                course._compute_temp_organization_ids()
            for student in org.student_ids:
                student._compute_temp_organizations()
            data_call_api = {
                "identifiers": (",").join(org.student_ids.mapped("email")),
                "course_code": (",").join(
                    org.course_ids.mapped("course_code")
                ),
                "action": "enroll",
            }
            return org.api_call(data_call_api)
        else:
            return org

    def write(self, vals):
        list_old_courses = self.course_ids
        old_courses = self.course_ids.ids  # list ids of old courses
        new_courses = (
            vals.get("course_ids")[0][2]
            if "course_ids" in vals
            else self.course_ids.ids
        )
        list_old_students = self.student_ids
        old_students = self.student_ids.ids  # list ids of old students
        # It is behavior of odoo, if just add and no remove it will use indicator 6 to link all id, if have remove or remove and add, it will use list of action with indicator 4 and 3
        if "student_ids" in vals:
            new_students = [
                sublist[1]
                for sublist in vals.get("student_ids")
                if sublist[0] == 4
            ]
            if vals.get("student_ids")[0][0] == 6:
                new_students = vals.get("student_ids")[0][2]
        else:
            new_students = self.student_ids.ids
        # unlink student have organization before add new organzation (unlink course of old organization as well)
        self.unlink_course_student_old_organization(old_students, new_students)

        # change data of organization officially
        result = super(StudentOrganization, self).write(vals)
        if old_courses != new_courses:
            self._onchange_course_ids(
                old_courses, new_courses, list_old_students
            )
        if old_students != new_students:
            self._onchange_student_ids(
                old_students, new_students, list_old_courses
            )
        return result

    def _onchange_course_ids(self, old_values, new_values, old_students):
        """
        A function that is called when the `course_ids` field of the current record is changed.
        param old_values: A list of the previous values of the `course_ids` field.
        param new_values: A list of the new values of the `course_ids` field.
        """
        added_courses = list(set(new_values) - set(old_values))
        removed_courses = list(set(old_values) - set(new_values))
        if len(removed_courses) != 0:
            for student in old_students:
                student.write(
                    {
                        "course_ids": [
                            (3, course_id) for course_id in removed_courses
                        ]
                    }
                )
            data_call_api = {
                "identifiers": (",").join(old_students.mapped("email")),
                "course_code": (",").join(
                    self.env["course_management"]
                    .browse(removed_courses)
                    .mapped("course_code")
                ),
                "action": "unenroll",
            }
            print(data_call_api)
            self.api_call(data_call_api)
        if len(added_courses) != 0:
            for student in self.student_ids:
                student.write(
                    {
                        "course_ids": [
                            (4, course_id) for course_id in added_courses
                        ]
                    }
                )
            data_call_api = {
                "identifiers": (",").join(self.student_ids.mapped("email")),
                "course_code": (",").join(
                    self.env["course_management"]
                    .browse(added_courses)
                    .mapped("course_code")
                ),
                "action": "enroll",
            }
            print(data_call_api)
            self.api_call(data_call_api)

    def _onchange_student_ids(self, old_values, new_values, old_courses):
        added_students = list(set(new_values) - set(old_values))
        removed_students = list(set(old_values) - set(new_values))
        if len(removed_students) != 0:
            for course in old_courses:
                course.write(
                    {
                        "student_ids": [
                            (3, student_id) for student_id in removed_students
                        ]
                    }
                )
            data_call_api = {
                "identifiers": (",").join(
                    self.env["portal.student"]
                    .browse(removed_students)
                    .mapped("email")
                ),
                "course_code": (",").join(old_courses.mapped("course_code")),
                "action": "unenroll",
            }
            print(data_call_api)
            self.api_call(data_call_api)
        if len(added_students) != 0:
            for course in self.course_ids:
                course.write(
                    {
                        "student_ids": [
                            (4, student_id) for student_id in added_students
                        ]
                    }
                )
            data_call_api = {
                "identifiers": (",").join(
                    self.env["portal.student"]
                    .browse(added_students)
                    .mapped("email")
                ),
                "course_code": (",").join(
                    self.course_ids.mapped("course_code")
                ),
                "action": "enroll",
            }
            print(data_call_api)
            self.api_call(data_call_api)

    def unlink_course_student_old_organization(
        self, old_students, new_students
    ):
        """
        Unlinks the given old_students from the old organization by removing them from the
        student_organization_student_ids field.
        """
        added_students = list(set(new_students) - set(old_students))
        list_students_enrolled_organization = self.env[
            "portal.student"
        ].search(
            [
                ("id", "in", added_students),
                ("student_organization_student_ids", "!=", False),
            ]
        )
        old_courses = set()
        for student in list_students_enrolled_organization:
            old_courses = old_courses | set(
                student.student_organization_student_ids.course_ids.ids
            )
            student.write(
                {
                    "student_organization_student_ids": False,
                    "course_ids": [
                        (3, course_id) for course_id in old_courses
                    ],
                },
            )
        print("old_courses", old_courses)
        data_call_api = {
            "identifiers": (",").join(
                self.env["portal.student"]
                .browse(added_students)
                .mapped("email")
            ),
            "course_code": (",").join(
                self.env["course_management"]
                .browse(old_courses)
                .mapped("course_code")
            ),
            "action": "unenroll",
        }
        print(data_call_api)
        self.api_call(data_call_api)

    def api_call(self, values):
        LMS_BASE = self.env[
            "service_key_configuration"
        ].get_api_key_by_service_name("LMS_BASE")
        API_BULK_ENROLL = self.env[
            "service_key_configuration"
        ].get_api_key_by_service_name("API_BULK_ENROLL")
        api_url = LMS_BASE + API_BULK_ENROLL
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "identifiers": values.get("identifiers"),
            "courses": values.get("course_code"),
            "auto_enroll": True,
            "email_students": False,
            "action": values.get("action"),
        }
        # if payload have identifiers and courses we will call api
        if payload.get("identifiers") and payload.get("courses"):
            try:
                response = requests.post(
                    api_url, json=payload, headers=headers
                )
                print(response)
                # Check the status code of the response
                if response.status_code == 200:
                    return self
                else:
                    print("test", response.json())
                    raise UserError(
                        f"API call failed with status code {response.status_code}, {(response.json()) if response.json() else 'asd'}"
                    )

            except requests.exceptions.RequestException as e:
                raise UserError(f"Error during API call: {e}")
        else:
            return
