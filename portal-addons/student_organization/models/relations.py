from odoo import models, fields, api
from odoo.exceptions import UserError
import requests


# Add Student Organization into student table
class StudentOrganization_Student(models.Model):
    _inherit = "portal.student"
    student_organization_student_ids = fields.Many2one(
        "student_organization",
        string="Student Organization",
    )
    temp_student_org = fields.Many2one(
        "student_organization",
        computed="_compute_temp_organization",
        string="Organization",
        store=False,
        default=lambda self: self.student_organization_student_ids,
    )

    # has_organization = fields.Boolean(
    #     string="Has Organization",
    #     compute="_compute_has_organization",
    #     store=False,
    #     readonly=True,
    # )

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
    @api.depends_context("open_form_event")
    def _compute_temp_organizations(self):
        for record in self:
            record.temp_student_org = record.student_organization_student_ids

    @api.onchange("student_organization_student_ids")
    def _onchange_organization_ids(self):
        """
        This function is an onchange handler for the field "student_organization_student_ids".
        It is triggered when the value of "student_organization_student_ids" is changed.
        Side Effects:
            - Updates the "course_ids" field of the current record with the course IDs of the added organizations.
            - Deletes the course IDs of the removed organizations from the "course_ids" field of the current record.
        """
        old_value = self.temp_student_org
        new_value = self.student_organization_student_ids
        print("org", old_value, new_value)
        if new_value != old_value:
            # compare to find any org added or removed. Replace old list by new list course_ids dont affect to courses_id enrolled individual
            added_courses = list(
                set(new_value.course_ids) - set(old_value.course_ids)
            )
            removed_courses = list(
                set(old_value.course_ids) - set(new_value.course_ids)
            )
            if len(removed_courses) != 0:
                self.write(
                    {
                        "course_ids": [
                            (3, course_id.id) for course_id in removed_courses
                        ]
                    }
                )
            if len(added_courses) != 0:
                self.write(
                    {
                        "course_ids": [
                            (4, course_id.id) for course_id in added_courses
                        ]
                    }
                )
        self._compute_temp_organizations()

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
                    raise UserError(
                        f"API call failed with status code {response.status_code}, {response.json() if response.json() else ''}"
                    )

            except requests.exceptions.RequestException as e:
                raise UserError(f"Error during API call: {e}")
        else:
            return


# Add student  into Student Organization table
class Student_Organization_Student(models.Model):
    _inherit = "student_organization"
    student_ids = fields.One2many(
        "portal.student",
        "student_organization_student_ids",
        string="Student List",
    )
