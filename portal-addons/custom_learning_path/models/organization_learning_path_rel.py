from odoo import models, fields, api


class OrgLearningPath(models.Model):
    _inherit = "organization_learning_path"

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    # course_ids = fields.Many2many(
    #     comodel_name="course_management",
    #     inverse_name="org_learning_path_id",
    #     string="Courses",
    #     # domain="[('organization_ids', '=', organization_id)]"
    # )

    course_ids = fields.Many2many(
        comodel_name="course_management",
        relation="org_learning_path_course",
        column1="org_learning_path_ids",
        column2="course_ids",
        string="Courses",
        domain="[('organization_ids.student_organization_id', '=', organization_id)]",
    )

    creator_id = fields.Many2one(
        comodel_name="portal.student",
        string="Creator",
        required=True,
        domain="[('student_organization_student_ids', '=', organization_id)]",
    )

    # editor_ids = fields.Many2many(
    #     comodel_name="portal.student",
    #     relation="editor_org_learning_path_rel",
    #     column1="org_learning_path_ids",
    #     column2="student_ids",
    #     string="Editors",
    #     domain="[('student_organization_student_ids', '=', organization_id)]",
    # )

    # featured_editor_ids = fields.Many2many(
    #     comodel_name="portal.student",
    #     relation="org_learning_path_featured_editor_rel",
    #     column1="org_learning_path_ids",
    #     column2="student_ids",
    #     string="Featured Editors",
    #     domain="[('student_organization_student_ids', '=', organization_id)]",
    # )


class Student(models.Model):
    _inherit = "portal.student"

    # # Many2many field for paths where the student is an editor
    # editor_org_learning_path_ids = fields.Many2many(
    #     comodel_name="organization_learning_path",
    #     relation="editor_org_learning_path_rel",
    #     column1="student_ids",
    #     column2="org_learning_path_ids",
    #     string="Edited Custom Learning Paths",
    # )

    # # Many2many field for paths where the student is a featured editor
    # featured_editor_org_learning_path_ids = fields.Many2many(
    #     comodel_name="organization_learning_path",
    #     relation="org_learning_path_featured_editor_rel",
    #     column1="student_ids",
    #     column2="org_learning_path_ids",
    #     string="Featured Editor Learning Paths",
    # )

    org_learning_path_ids = fields.One2many(
        comodel_name="organization_learning_path",
        inverse_name="creator_id",
        string="Organization Learning Paths Created",
    )


class CourseManagement(models.Model):
    _inherit = "course_management"

    org_learning_path_ids = fields.Many2many(
        comodel_name="organization_learning_path",
        relation="org_learning_path_course",
        column1="course_ids",
        column2="org_learning_path_ids",
        string="Organization Learning Paths",
    )


class StudentOrganization(models.Model):
    _inherit = "student_organization"

    org_learning_path_ids = fields.One2many(
        comodel_name="organization_learning_path",
        inverse_name="organization_id",
        string="Organization Learning Paths",
    )
