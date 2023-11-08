from odoo import fields, models


class StudentCourse(models.Model):
    _name = "student.course"
    _description = "Student Course Relationship"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    course_id = fields.Many2one(
        "course_management", string="Course", required=True
    )
