from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


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

    is_active = fields.Boolean(string="Is Active", default=True)


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
        domain="[('is_active', '=', True)]",
    )

    def _compute_organization_learning_programs(self):
        _logger.info("POLP: Computing organization learning programs")
        for student in self:
            _logger.info(
                "POLP: Computing organization learning programs for %s",
                student.name,
            )
            try:
                if student.student_organization_student_ids:
                    _logger.info(
                        "POLP: Searching organization learning programs for %s",
                        student.name,
                    )
                    org_id = student.student_organization_student_ids.id
                    _logger.info("POLP: Organization ID: %s", org_id)

                    _logger.info(
                        "POLP: Searching access records for organization"
                    )
                    access_records = self.env[
                        "organization_polp_access"
                    ].search([("organization_id", "=", org_id)])

                    _logger.info("POLP: Access records found")
                    _logger.debug("POLP: Access records: %s", access_records)

                    _logger.info("POLP: Mapped access records")
                    learning_program_ids = access_records.mapped(
                        "po_learning_program_id.id"
                    )
                    _logger.debug(
                        "POLP: Learning program IDs: %s", learning_program_ids
                    )

                    _logger.info(
                        "POLP: Setting organization learning programs"
                    )
                    student.organization_learning_programs = [
                        (6, 0, learning_program_ids)
                    ]
                    _logger.info(
                        "POLP: Organization learning programs set successfully"
                    )
                    _logger.info(
                        "POLP: Finished processing student: %s", student.name
                    )
                    _logger.debug(
                        "POLP: Organization learning programs: %s",
                        student.organization_learning_programs,
                    )
                else:
                    _logger.info(
                        "POLP: No organization learning programs found for %s",
                        student.name,
                    )

                    student.organization_learning_programs = [(6, 0, [])]
                    _logger.debug(
                        "POLP: Organization learning programs: %s",
                        student.organization_learning_programs,
                    )
            except Exception:
                _logger.error(
                    "POLP: Error while computing organization learning programs for %s",
                    student.name,
                )
                student.organization_learning_programs = [(6, 0, [])]
                # Log the exception if needed

    def _compute_individual_learning_programs(self):
        _logger.info("POLP: Computing individual learning programs")
        for student in self:
            _logger.info(
                "POLP: Computing individual learning programs for %s",
                student.name,
            )
            try:
                _logger.info(
                    "POLP: Checking if student is an individual student"
                )
                if not student.student_organization_student_ids:
                    _logger.info(
                        "POLP: Student is an individual student. Searching access records for individual"
                    )

                    access_records = self.env["individual_polp_access"].search(
                        [("individual_student_id", "=", student.id)]
                    )
                    _logger.info("POLP: Access records found")
                    _logger.debug("POLP: Access records: %s", access_records)

                    _logger.info("POLP: Mapping access records")
                    learning_program_ids = access_records.mapped(
                        "po_learning_program_id.id"
                    )
                    _logger.debug(
                        "POLP: Learning program IDs: %s", learning_program_ids
                    )

                    _logger.info("POLP: Setting individual learning programs")
                    student.individual_learning_programs = [
                        (6, 0, learning_program_ids)
                    ]
                    _logger.info(
                        "POLP: Individual learning programs set successfully"
                    )
                    _logger.info(
                        "POLP: Finished processing student: %s", student.name
                    )
                else:
                    _logger.info(
                        "POLP: Student is an organization student. Skipping individual learning programs"
                    )
                    student.individual_learning_programs = [(6, 0, [])]
            except Exception:
                _logger.error(
                    "POLP: Error while computing individual learning programs for %s",
                    student.name,
                )
                student.individual_learning_programs = [(6, 0, [])]

    def _compute_accessible_courses(self):
        _logger.info("POLP: Computing accessible courses")
        for student in self:
            _logger.info(
                "POLP: Computing accessible courses for %s", student.name
            )
            try:
                _logger.info("POLP: Checking if student is in an organization")
                if student.student_organization_student_ids:
                    _logger.info("POLP: Student is in an organization")
                    org_id = student.student_organization_student_ids.id
                    _logger.info("POLP: Organization ID: %s", org_id)
                    # Filter only active course access records for the organization
                    _logger.info(
                        "POLP: Searching course access records for organization"
                    )
                    course_access_records = self.env[
                        "organization_course_access"
                    ].search(
                        [
                            ("student_organization_id", "=", org_id),
                            ("is_active", "=", True),
                        ]
                    )
                    _logger.info("POLP: Course access records found")
                    _logger.debug(
                        "POLP: Course access records: %s",
                        course_access_records,
                    )
                else:
                    # Filter only active course access records for individual students
                    _logger.info(
                        "POLP: Student is an individual. Searching course access records for individual"
                    )
                    _logger.info(
                        "POLP: Searching course access records for individual"
                    )
                    course_access_records = self.env[
                        "individual_course_access"
                    ].search(
                        [
                            ("individual_student_id", "=", student.id),
                            ("is_active", "=", True),
                        ]
                    )
                    _logger.info("POLP: Course access records found")
                    _logger.debug(
                        "POLP: Course access records: %s",
                        course_access_records,
                    )
                # Get IDs of all active courses
                _logger.info("POLP: Mapping course access records")
                course_ids = course_access_records.mapped(
                    "purchased_course_id.id"
                )
                _logger.debug("POLP: Course IDs: %s", course_ids)

                _logger.info("POLP: Setting accessible courses")
                student.accessible_courses = [(6, 0, course_ids)]
                _logger.info("POLP: Accessible courses set successfully")
                _logger.info(
                    "POLP: Finished processing student: %s", student.name
                )
            except Exception:
                _logger.error(
                    "POLP: Error while computing accessible courses for %s",
                    student.name,
                )
                student.accessible_courses = [(6, 0, [])]
