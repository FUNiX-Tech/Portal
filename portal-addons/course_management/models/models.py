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
    student_ids = fields.Many2many(
        "portal.student",
        relation="courses_enroll_students",
        column1="course_ids",
        column2="student_ids",
        string="Courses enrolled to Students",
    )

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(course_management, self).create(vals)
