# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StudentGroupCourseAssignment(models.Model):
    _name = "student_group_course_assignment"

    name = fields.Char(string="Name", required=True)

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    student_group_id = fields.Many2one(
        comodel_name="student_group",
        string="Student Group",
        required=True,
        domain="[('group_organization_id', '=', organization_id)]",
    )

    course_id = fields.Many2one(
        comodel_name="course_management",
        string="Course",
        required=True,
        domain="[('organization_ids.student_organization_id', '=', organization_id)]",
    )

    assigned_by = fields.Many2one(
        comodel_name="portal.student",
        string="Assigned By",
        required=True,
        domain="['&', ('student_organization_student_ids', '=', organization_id), ('student_role_id.name', '=', 'ADMIN')]",
    )

    assigned_date = fields.Date(
        string="Assigned Date", required=True, default=fields.Date.today()
    )

    assigned_description = fields.Html(string="Assigned Description")


class StudentGroupCourseGroupAssignment(models.Model):
    _name = "student_group_course_group_assignment"

    name = fields.Char(string="Name", required=True)

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    student_group_id = fields.Many2one(
        comodel_name="student_group",
        string="Student Group",
        required=True,
        domain="[('group_organization_id', '=', organization_id)]",
    )

    course_group_id = fields.Many2one(
        comodel_name="organization_course_group",
        string="Course Group",
        required=True,
        domain="[('organization_id', '=', organization_id)]",
    )

    assigned_by = fields.Many2one(
        comodel_name="portal.student",
        string="Assigned By",
        required=True,
        domain="['&', ('student_organization_student_ids', '=', organization_id), ('student_role_id.name', '=', 'ADMIN')]",
    )

    assigned_date = fields.Date(
        string="Assigned Date", required=True, default=fields.Date.today()
    )

    assigned_description = fields.Html(string="Assigned Description")
