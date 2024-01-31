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

    @api.onchange('student_organization_student_ids')
    def _onchange_student_organization_student_ids(self):
        # Check if the student has an organization
        if self.student_organization_student_ids:
            # Find or create the 'USER' role
            user_role = self.env['student_role'].search([('name', '=', 'USER')], limit=1)
            print('user_role', user_role)
            if not user_role:
                print('This user_role', user_role)
                user_role = self.env['student_role'].create({'name': 'USER', 'description': 'User Role'})

            # Set the 'USER' role as the default role
            self.student_role_id = user_role.id