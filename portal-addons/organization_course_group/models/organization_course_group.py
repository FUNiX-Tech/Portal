# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OrganizationCourseGroup(models.Model):
    _name = "organization_course_group"
    _description = "Course Group created by Admin"

    name = fields.Char()
    description = fields.Html()

    creator_id = fields.Many2one(
        comodel_name="portal.student",
        string="Creator",
        required=True,
        domain="['|',('student_organization_student_ids', '=', False), ('student_organization_student_ids', '=', organization_id), ('student_role_id.name','=', 'ADMIN')]",
    )

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    course_ids = fields.Many2many(
        comodel_name="course_management",
        relation="organization_course_group_course",
        column1="organization_course_group_ids",
        column2="course_ids",
        string="Courses",
        domain="[('organization_ids.student_organization_id', '=', organization_id)]",
    )
