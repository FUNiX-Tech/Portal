from odoo import models, fields, api

from datetime import datetime


class OrganizationCourseAccess(models.Model):
    _name = "organization_course_access"
    _description = "Organization Course Access"

    student_organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Student Organization",
        required=True,
    )

    student_organization_name = fields.Char(
        related="student_organization_id.name",
        string="Organization Name",
    )

    purchased_course_id = fields.Many2one(
        comodel_name="course_management",
        string="Purchased Course",
        required=True,
    )

    course_name = fields.Char(
        related="purchased_course_id.course_name",
    )

    is_single_course = fields.Boolean(string="Is Single Course", default=False)

    is_active = fields.Boolean(string="Is Active", default=True)


class IndividualCourseAccess(models.Model):
    _name = "individual_course_access"
    _description = "Individual Course Access"

    individual_student_id = fields.Many2one(
        comodel_name="portal.student",
        string="Individual Student",
        required=True,
        domain="[('student_organization_student_ids', '=', False)]",
    )

    name = fields.Char(
        related="individual_student_id.name",
        string="Student Name",
    )

    purchased_course_id = fields.Many2one(
        comodel_name="course_management",
        string="Purchased Course",
        required=True,
    )

    course_name = fields.Char(
        related="purchased_course_id.course_name",
    )

    is_single_course = fields.Boolean(string="Is Single Course", default=False)

    is_active = fields.Boolean(string="Is Active", default=True)
