from odoo import models, fields, api


# Add Student group into student table
class StudentGroup_Student(models.Model):
    _inherit = "portal.student"
    student_group_student_ids = fields.Many2many(
        "student_group",
        "student_group_student_rel",
        "student_id",
        "student_group__id",
        string="Student Group",
    )


# Add student list into Student Group table
class Student_GroupStudent(models.Model):
    _inherit = "student_group"
    student_ids = fields.Many2many(
        "portal.student",
        "student_group_student_rel",
        "student_group__id",
        "student_id",
        string="Student List",
    )


# Add student group into Course table
class Course_Student_Group(models.Model):
    _inherit = "course_management"
    student_group_course_ids = fields.Many2many(
        "student_group",
        "student_group_course_rel",
        "course_id",
        "student_group__id",
        string="Student Group",
    )

    # integrate students in group with student enrolled /unenrolled
    @api.onchange("student_group_course_ids")
    def onchange_student_group_course_ids(self):
        if self.student_group_course_ids:
            self.student_ids = self.student_group_course_ids.mapped(
                "student_ids"
            )
        else:
            self.student_ids = False


# Add course list into Student Group table
class Student_Group_Course(models.Model):
    _inherit = "student_group"
    course_ids = fields.Many2many(
        "course_management",
        "student_group_course_rel",
        "student_group__id",
        "course_id",
        string="Course List",
    )
    # When remove course in Student Group
    # @api.onchange('course_ids')
    # def onchange_course_ids(self):
    #     if self.course_ids:
    #         self.student_group_course_ids = self.course_ids.mapped('student_group_course_ids')
    #     else:
    #         self.student_group_course_ids = False
