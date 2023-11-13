from odoo import models, fields, api


# Add Student Organization into student table
class StudentOrganization_Student(models.Model):
    _inherit = "portal.student"
    student_organization_student_ids = fields.Many2many(
        "student_organization",
        "student_organization_student_rel",
        "student_id",
        "student_organization_id",
        string="Student Organization",
    )


# Add student  into Student Organization table
class Student_Organization_Student(models.Model):
    _inherit = "student_organization"
    student_ids = fields.Many2many(
        "portal.student",
        "student_organization_student_rel",
        "student_organization_id",
        "student_id",
        string="Student List",
    )
