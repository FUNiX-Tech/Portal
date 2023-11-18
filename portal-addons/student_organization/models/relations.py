from odoo import models, fields, api
from odoo.exceptions import UserError
import requests


# Add Student Organization into student table
class StudentOrganization_Student(models.Model):
    _inherit = "portal.student"
    student_organization_student_ids = fields.Many2many(
        "student_organization",
        "student_organization_student_rel",
        "student_id",
        "student_organization_id",
        string="Student Organization",
    )
    temp_student_orgs = fields.Many2many(
        "student_organization",
        computed="_compute_temp_organizations",
        string="Temporary Student Organizations",
    )

    @api.model
    def create(self, vals):
        student = super(StudentOrganization_Student, self).create(vals)
        if len(student.course_ids.ids) != 0:
            data_call_api = {
                "identifiers": student.email,
                "course_code": (",").join(
                    student.course_ids.mapped("course_code")
                ),
                "action": "enroll",
            }
            return student.api_call(data_call_api)
        else:
            return student

    def write(self, vals):
        old_courses = self.course_ids
        success = super(StudentOrganization_Student, self).write(vals)
        new_courses = self.course_ids
        if old_courses != new_courses:
            added_courses = list(set(new_courses) - set(old_courses))
            remove_courses = list(set(old_courses) - set(new_courses))
            if len(added_courses) != 0:
                data_call_api = {
                    "identifiers": self.email,
                    "course_code": (",").join(
                        map(lambda c: c.course_code, added_courses)
                    ),
                    "action": "enroll",
                }
                self.api_call(data_call_api)
            if len(remove_courses) != 0:
                data_call_api = {
                    "identifiers": self.email,
                    "course_code": (",").join(
                        map(lambda c: c.course_code, remove_courses)
                    ),
                    "action": "unenroll",
                }
                self.api_call(data_call_api)
            return success
        else:
            return success

    @api.depends("student_organization_student_ids")
    def _compute_temp_organizations(self):
        self.temp_student_orgs = self.student_organization_student_ids

    @api.onchange("student_organization_student_ids")
    def _onchange_organization_ids(self):
        """
        This function is an onchange handler for the field "student_organization_student_ids".
        It is triggered when the value of "student_organization_student_ids" is changed.
        Side Effects:
            - Updates the "course_ids" field of the current record with the course IDs of the added organizations.
            - Deletes the course IDs of the removed organizations from the "course_ids" field of the current record.
        """
        old_values = self.temp_student_orgs
        new_values = self.student_organization_student_ids
        added_orgs = list(set(new_values) - set(old_values))
        removed_orgs = list(set(old_values) - set(new_values))
        if len(added_orgs) != 0:
            for org in added_orgs:
                self.write(
                    {
                        "course_ids": [
                            (4, course_id) for course_id in org.course_ids.ids
                        ]
                    }
                )
        if len(removed_orgs) != 0:
            for org in removed_orgs:
                self.write(
                    {
                        "course_ids": [
                            (3, course_id) for course_id in org.course_ids.ids
                        ]
                    }
                )
        self._compute_temp_organizations()

    def api_call(self, values):
        api_url = (
            "https://test-xseries.funix.edu.vn/api/bulk_enroll/v1/bulk_enroll"
        )
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
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            print(response)
            # Check the status code of the response
            if response.status_code == 200:
                return self
            else:
                raise UserError(
                    f"API call failed with status code {response.status_code}, {response.json()}"
                )

        except requests.exceptions.RequestException as e:
            raise UserError(f"Error during API call: {e}")


# Add student  into Student Organization table
class Student_Organization_Student(models.Model):
    _inherit = "student_organization"
    student_ids = fields.Many2many(
        "portal.student",
        "student_organization_student_rel",
        "student_organization_id",
        "student_id",
        string="Student List",
    )
