from odoo import models, fields


class Student(models.Model):
    _inherit = "portal.student"

    course_ids = fields.Many2many(
        "course_management",
        "student_course_rel",
        "student_id",
        "course_id",
        string="Courses",
    )
