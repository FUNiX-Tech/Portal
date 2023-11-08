from odoo import models, fields, api

from datetime import datetime


class LearningProgram(models.Model):
    _name = "learning_program"
    _description = "Learning Program"

    name = fields.Char(string="name", required=True)
    student_list = fields.Many2many(
        "portal.student",
        relation="group_learning_program_students_relation",
        column1="learning_program_ids",
        column2="student_ids",
        string="Student List",
    )
    course_list = fields.Many2many(
        "course_management",
        relation="group_learning_program_courses_relation",
        column1="learning_program_ids",
        column2="course_ids",
        string="Course List",
    )
    creator = fields.Char(
        string="creator", default=lambda self: self.env.user.name
    )
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )

    desc = fields.Text(string="description")

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(LearningProgram, self).create(vals)
