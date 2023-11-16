# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


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
    )

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        course = super(course_management, self).create(vals)
        if len(course.student_ids.ids) != 0:
            pass
        return course

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
        self._compute_temp_organization_ids()
