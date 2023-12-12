from odoo import fields, models


class StudentCourse(models.Model):
    _name = "student.course"
    _description = "Student Course Relationship"
    _table = "student_course_rel"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    course_id = fields.Many2one(
        "course_management", string="Course", required=True
    )
    # Define a unique SQL constraint
    _sql_constraints = [
        (
            "unique_student_course",
            "UNIQUE(student_id, course_id)",
            "Student can only be assigned to a course once.",
        )
    ]
    progress = fields.Char(string="Course Progress")
