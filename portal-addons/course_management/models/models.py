# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
import requests


# Model course
class course_management(models.Model):
    _name = "course_management"
    _description = "Course Management"
    _rec_name = "course_name"

    course_code = fields.Char(string="Course Code", required=True)
    course_name = fields.Char(string="Course Name", required=True)
    course_creator = fields.Many2one(
        "res.users", string="Course creator", required=True
    )
    course_desc = fields.Text(string="Course Description")
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )
    organization_ids = fields.Many2many(
        comodel_name="student_organization",
        relation="courses_enroll_organizations",
        column1="course_ids",
        column2="organization_ids",
        string="Courses enrolled to Organizations",
    )
    temp_organization_ids = fields.Many2many(
        comodel_name="student_organization",
        computed="_compute_temp_organization_ids",
        string="Temporary Organizations",
        store=False,
        default=lambda self: self.organization_ids,
    )

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        course = super(course_management, self).create(vals)
        if len(course.student_ids.ids) != 0:
            data_call_api = {
                "identifiers": (",").join(course.student_ids.mapped("email")),
                "course_code": course.course_code,
                "action": "enroll",
            }
            try:
                response = self.api_call(data_call_api)
                if response.get("status_code") != 200:
                    raise UserError(response.get("message"))
                else:
                    return course
            except UserError as e:
                raise UserError(f"{e}. Please contact administrator for help.")

        else:
            return course

    def write(self, vals):
        old_students = self.student_ids
        success = super(course_management, self).write(vals)
        new_students = self.student_ids
        if old_students != new_students:
            try:
                added_students = list(set(new_students) - set(old_students))
                remove_students = list(set(old_students) - set(new_students))
                if len(remove_students) != 0:
                    data_call_api = {
                        "identifiers": (",").join(
                            map(lambda s: s.email, remove_students)
                        ),
                        "course_code": self.course_code,
                        "action": "unenroll",
                    }
                    response = self.api_call(data_call_api)
                    if response.get("status_code") != 200:
                        raise UserError(response.get("message"))
                if len(added_students) != 0:
                    data_call_api = {
                        "identifiers": (",").join(
                            map(lambda s: s.email, added_students)
                        ),
                        "course_code": self.course_code,
                        "action": "enroll",
                    }
                    response = self.api_call(data_call_api)
                    if response.get("status_code") != 200:
                        raise UserError(response.get("message"))
                return success
            except UserError as e:
                raise UserError(f"{e}. Please contact administrator for help.")
        else:
            return success

    @api.depends("organization_ids")
    def _compute_temp_organization_ids(self):
        self.temp_organization_ids = self.organization_ids

    @api.onchange("organization_ids")
    def _onchange_organization_ids(self):
        """
        This function is an onchange method that is triggered whenever the value of the field "organization_ids" changes.
        It updates the "student_ids" field based on the changes in the "organization_ids" field.
        """
        old_values = self.temp_organization_ids
        new_values = self.organization_ids
        added_orgs = list(set(new_values) - set(old_values))
        removed_orgs = list(set(old_values) - set(new_values))
        if len(removed_orgs) != 0:
            for org in removed_orgs:
                self.write(
                    {
                        "student_ids": [
                            (3, student_id)
                            for student_id in org.student_ids.ids
                        ]
                    }
                )
        if len(added_orgs) != 0:
            for org in added_orgs:
                self.write(
                    {
                        "student_ids": [
                            (4, student_id)
                            for student_id in org.student_ids.ids
                        ]
                    }
                )

        self._compute_temp_organization_ids()

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
                    return {
                        "message": "API call successful",
                        "status_code": 200,
                    }
                else:
                    return {
                        "message": f"API call failed with status code {response.status_code}, {response.json() if response.json() else ''}",
                        "status_code": response.status_code,
                    }

            except requests.exceptions.RequestException as e:
                return {
                    "message": f"Error during API call: {e}",
                    "status_code": response.status_code,
                }
        else:
            return
