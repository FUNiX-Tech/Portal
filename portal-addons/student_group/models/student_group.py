from odoo import models, fields, api
from datetime import datetime


class StudentGroup(models.Model):
    _name = "student_group"
    _description = "Student Group"

    name = fields.Char(string="name", required=True)
    student_list = fields.Many2many(
        "portal.student",
        relation="group_students_relation",
        column1="group_ids",
        column2="student_ids",
        string="Student List",
    )
    course_list = fields.Many2many(
        "course_management",
        relation="group_courses_relation",
        column1="student_group_ids",
        column2="course_ids",
        string="Course List",
    )
    creator = fields.Char(
        string="creator", default=lambda self: self.env.user.name
    )
    group_note = fields.Text(string="group_note")
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(StudentGroup, self).create(vals)
