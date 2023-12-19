from odoo import models, fields, api


class IndividualLearningPath(models.Model):
    _inherit = "individual_learning_path"

    course_ids = fields.Many2many(
        comodel_name="course_management",
        relation="individual_learning_path_course",
        column1="individual_learning_path_ids",
        column2="course_ids",
        string="Courses",
        domain="[('individual_student_ids.individual_student_id', '=', creator_id)]",
    )

    creator_id = fields.Many2one(
        comodel_name="portal.student",
        string="Student",
        required=True,
        domain="[('student_organization_student_ids', '=', False)]",
    )


class Student(models.Model):
    _inherit = "portal.student"

    # Existing field for paths created by the student
    individual_learning_path_ids = fields.One2many(
        comodel_name="individual_learning_path",
        inverse_name="creator_id",
        string="Created Custom Learning Paths",
        domain="[('is_active', '=', True)]",
    )


class CourseManagement(models.Model):
    _inherit = "course_management"

    individual_learning_path_id = fields.Many2many(
        comodel_name="individual_learning_path",
        relation="individual_learning_path_course",
        column1="course_ids",
        column2="individual_learning_path_ids",
        string="Individual Learning Paths",
        domain="[('is_active', '=', True)]",
    )
