from odoo import models, fields


class CourseManagement(models.Model):
    _inherit = "course_management"

    student_ids = fields.Many2many(
        "portal.student",
        "student_course_rel",
        "course_id",
        "student_id",
        string="Students Enrolled",
    )
