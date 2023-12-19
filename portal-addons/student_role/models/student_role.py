# -*- coding: utf-8 -*-

from odoo import models, fields, api


# StudentRole model
class StudentRole(models.Model):
    _name = "student_role"
    _description = "Student Role in Organization"

    name = fields.Char(
        string="Role Name",
        required=True,
    )
    description = fields.Html(
        string="Role Description",
    )

    business_student_ids = fields.One2many(
        comodel_name="portal.student",
        inverse_name="student_role_id",
        string="Business Students",
        domain="[('student_organization_student_ids', '=', True)]",
    )


# Student model
class Student(models.Model):
    _inherit = "portal.student"

    student_role_id = fields.Many2one(
        comodel_name="student_role",
        string="Student Role",
    )
