from odoo import models, fields, api


class CourseManagement(models.Model):
    _inherit = "course_management"

    organization_ids = fields.One2many(
        comodel_name="organization_course_access",
        inverse_name="purchased_course_id",
        string="Organizations",
        domain="[('is_active', '=', True)]",
    )

    individual_student_ids = fields.One2many(
        comodel_name="individual_course_access",
        inverse_name="purchased_course_id",
        string="Individual Students",
        domain="[('is_active', '=', True)]",
    )

    po_learning_program_ids = fields.Many2many(
        comodel_name="po_learning_program",
        relation="po_learning_program_course",
        column1="course_ids",
        column2="po_learning_program_ids",
    )


class StudentOrganization(models.Model):
    _inherit = "student_organization"

    purchased_po_learning_program_ids = fields.One2many(
        comodel_name="organization_polp_access",
        inverse_name="organization_id",
        string="Purchased PO Learning Programs",
    )

    course_access_ids = fields.One2many(
        comodel_name="organization_course_access",
        inverse_name="student_organization_id",
        string="Course Access",
        domain="[('is_active', '=', True)]",
    )


class Student(models.Model):
    _inherit = "portal.student"

    # Computed fields for learning programs and courses
    organization_learning_programs = fields.One2many(
        "po_learning_program",
        compute="_compute_organization_learning_programs",
        string="Organization Learning Programs",
    )
    individual_learning_programs = fields.One2many(
        "po_learning_program",
        compute="_compute_individual_learning_programs",
        string="Individual Learning Programs",
    )
    accessible_courses = fields.One2many(
        "course_management",
        compute="_compute_accessible_courses",
        string="Accessible Courses",
    )

    def _compute_organization_learning_programs(self):
        for student in self:
            try:
                if student.student_organization_student_ids:
                    org_id = student.student_organization_student_ids.id
                    access_records = self.env[
                        "organization_polp_access"
                    ].search([("organization_id", "=", org_id)])
                    learning_program_ids = access_records.mapped(
                        "po_learning_program_id.id"
                    )
                    student.organization_learning_programs = [
                        (6, 0, learning_program_ids)
                    ]
                else:
                    student.organization_learning_programs = [(6, 0, [])]
            except Exception:
                student.organization_learning_programs = [(6, 0, [])]
                # Log the exception if needed

    def _compute_individual_learning_programs(self):
        for student in self:
            try:
                if not student.student_organization_student_ids:
                    access_records = self.env["individual_polp_access"].search(
                        [("individual_student_id", "=", student.id)]
                    )
                    learning_program_ids = access_records.mapped(
                        "po_learning_program_id.id"
                    )
                    student.individual_learning_programs = [
                        (6, 0, learning_program_ids)
                    ]
                else:
                    student.individual_learning_programs = [(6, 0, [])]
            except Exception:
                student.individual_learning_programs = [(6, 0, [])]

    def _compute_accessible_courses(self):
        for student in self:
            try:
                if student.student_organization_student_ids:
                    org_id = student.student_organization_student_ids.id
                    course_access_records = self.env[
                        "organization_course_access"
                    ].search([("student_organization_id", "=", org_id)])
                else:
                    course_access_records = self.env[
                        "individual_course_access"
                    ].search([("individual_student_id", "=", student.id)])
                course_ids = course_access_records.mapped(
                    "purchased_course_id.id"
                )
                student.accessible_courses = [(6, 0, course_ids)]
            except Exception:
                student.accessible_courses = [(6, 0, [])]
