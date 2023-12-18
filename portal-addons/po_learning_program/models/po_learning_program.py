from odoo import models, fields, api

from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class LearningProgram(models.Model):
    _name = "po_learning_program"
    _description = "Platform Owner Learning Program"

    name = fields.Char(string="name", required=True)

    course_list = fields.Many2many(
        "course_management",
        relation="po_learning_program_course",
        column1="po_learning_program_ids",
        column2="course_ids",
        string="Course List",
    )

    creator = fields.Many2one(
        "res.users",
        string="LP Author",
    )

    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )

    desc = fields.Text(string="description")

    old_course_list = fields.Many2many(
        "course_management",
        string="Old Course List",
        compute="_compute_old_course_list",
    )

    organization_ids = fields.One2many(
        comodel_name="organization_polp_access",
        inverse_name="po_learning_program_id",
        string="Organizations",
    )

    individual_student_ids = fields.One2many(
        comodel_name="individual_polp_access",
        inverse_name="po_learning_program_id",
        string="Individual Students",
    )

    @api.model
    def create(self, vals):
        _logger.info("POLP: Creating new learning program")
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(LearningProgram, self).create(vals)

    @api.depends("course_list")
    def _compute_old_course_list(self):
        _logger.info("POLP: Computing old course list")
        for record in self:
            if record._origin.course_list:
                _logger.info("POLP: Old course list exists")
                record.old_course_list = record._origin.course_list
                _logger.debug(
                    "POLP: Old course list: %s", record.old_course_list
                )
            else:
                _logger.info("POLP: Old course list is empty")
                record.old_course_list = []

    def add_courses_to_learning_program(self, new_course_ids):
        _logger.info("POLP: Adding new courses to PO learning program")
        if not new_course_ids:
            _logger.info("POLP: No new courses to add")
            return

        if not self._origin.id:
            _logger.info("POLP: No PO learning program ID")
            return

        # Before executing raw SQL, flush the ORM to ensure data consistency
        _logger.debug("POLP: Flushing the ORM")
        self.env.cr.flush()

        print("self._origin.id", self._origin.id)
        _logger.info("POLP: PO Learning Program ID: %s", self._origin.id)
        # Current po learning program id

        # Find organizations that have access to this learning program
        _logger.info("POLP: Fetching organization IDs")
        query = """
            SELECT organization_id
            FROM organization_polp_access
            WHERE po_learning_program_id = %s and is_active = %s;
        """
        self._cr.execute(query, (self._origin.id, "true"))
        organization_ids = [row[0] for row in self._cr.fetchall()]
        _logger.info("POLP: Fetched organization IDs completed ")
        _logger.debug("POLP: Organization IDs: %s", organization_ids)
        for org_id in organization_ids:
            # Check and update existing course access or add new access
            _logger.info(
                "POLP: Checking and updating existing course access or adding new access for organization %s",
                org_id,
            )
            for course_id in new_course_ids:
                _logger.info(
                    "POLP: Checking course access for organization %s and course %s",
                    org_id,
                    course_id,
                )

                _logger.debug(
                    "POLP: Querying course access table for organization %s and course %s",
                    org_id,
                    course_id,
                )
                query = """
                    SELECT id, is_active
                    FROM organization_course_access
                    WHERE student_organization_id = %s AND purchased_course_id = %s;
                """
                self._cr.execute(query, (org_id, course_id))
                result = self._cr.fetchone()
                _logger.debug("POLP: Query result: %s", result)

                if result:
                    _logger.info(
                        "POLP: Course access found for organization %s and course %s",
                        org_id,
                        course_id,
                    )
                    access_id, is_active = result
                    if not is_active:
                        _logger.info(
                            "POLP: Reactivating course access for organization %s and course %s",
                            org_id,
                            course_id,
                        )
                        # Reactivate the inactive course
                        _logger.debug(
                            "POLP: Reactivating course access with ID %s",
                            access_id,
                        )
                        update_query = """
                            UPDATE organization_course_access
                            SET is_active = TRUE
                            WHERE id = %s;
                        """
                        self._cr.execute(update_query, (access_id,))
                        _logger.info(
                            "POLP: Reactivated course access for organization %s and course %s",
                            org_id,
                            course_id,
                        )

                else:
                    # Insert new course access
                    _logger.info(
                        "POLP: Course access not found for organization %s and course %s",
                        org_id,
                        course_id,
                    )
                    _logger.info(
                        "POLP: Inserting new course access for organization %s and course %s",
                        org_id,
                        course_id,
                    )
                    insert_query = """
                        INSERT INTO organization_course_access (student_organization_id, purchased_course_id, is_single_course, is_active)
                        VALUES (%s, %s, FALSE, TRUE);
                    """
                    self._cr.execute(insert_query, (org_id, course_id))
                    _logger.info(
                        "POLP: Inserted new course access for organization %s and course %s",
                        org_id,
                        course_id,
                    )

        self._cr.commit()

    def remove_courses_from_learning_program(self, old_course_ids):
        _logger.info("POLP: Removing old courses from PO learning program")
        if not old_course_ids:
            _logger.info("POLP: No old courses to remove")
            return

        # Flush the ORM before executing raw SQL
        _logger.debug("POLP: Flushing the ORM")
        self.env.cr.flush()

        # Find organizations that have access to this learning program
        _logger.info("POLP: Fetching organization IDs")
        query = """
            SELECT organization_id
            FROM organization_polp_access
            WHERE po_learning_program_id = %s
        """
        self._cr.execute(query, (self._origin.id,))
        organization_ids = [row[0] for row in self._cr.fetchall()]
        _logger.info("POLP: Fetched organization IDs completed")
        _logger.debug("POLP: Organization IDs: %s", organization_ids)

        for org_id in organization_ids:
            _logger.info("POLP: Checking organization %s", org_id)
            for course_id in old_course_ids:
                _logger.info(
                    "POLP: Checking course access for organization %s and course %s",
                    org_id,
                    course_id,
                )
                # Check if the course is part of other learning programs

                _logger.debug(
                    "POLP: Check if course %s is part of other learning programs",
                    course_id,
                )
                check_query = """
                    SELECT COUNT(*)
                    FROM organization_polp_access opa
                    JOIN po_learning_program_course plpc ON opa.po_learning_program_id = plpc.po_learning_program_ids
                    WHERE opa.organization_id = %s AND plpc.course_ids = %s AND opa.po_learning_program_id != %s;
                """
                self._cr.execute(
                    check_query, (org_id, course_id, self._origin.id)
                )
                count = self._cr.fetchone()[0]
                _logger.debug(
                    "POLP: Number of other learning programs that use the course: %s",
                    count,
                )

                if count == 0:
                    _logger.info(
                        "POLP: Course %s is not in other learning programs",
                        course_id,
                    )
                    _logger.info(
                        "POLP: Checking if course %s is purchased separately",
                        course_id,
                    )
                    # Check if the course is purchased separately
                    _logger.debug(
                        "POLP: Querying if course %s is purchased separately",
                        course_id,
                    )
                    check_query = """
                        SELECT is_single_course
                        FROM organization_course_access
                        WHERE student_organization_id = %s AND purchased_course_id = %s;
                    """
                    self._cr.execute(check_query, (org_id, course_id))
                    is_single_course = self._cr.fetchone()[0]
                    _logger.debug(
                        "POLP: Is single course: %s", is_single_course
                    )

                    if not is_single_course:
                        _logger.info(
                            "POLP: Course %s is not purchased separately",
                            course_id,
                        )
                        # Set course to inactive
                        _logger.debug(
                            "POLP: Setting course %s to inactive", course_id
                        )
                        update_query = """
                            UPDATE organization_course_access
                            SET is_active = FALSE
                            WHERE student_organization_id = %s AND purchased_course_id = %s;
                        """
                        self._cr.execute(update_query, (org_id, course_id))
                        _logger.info(
                            "POLP: Set course %s to inactive", course_id
                        )

        self._cr.commit()

    def add_courses_to_individuals_learning_program(self, new_course_ids):
        _logger.info("POLP: Adding new courses to individuals")
        if not new_course_ids:
            _logger.info("POLP: No new courses to add")
            return

        if not self._origin.id:
            _logger.info("POLP: PO learning program has no ID")
            return

        # Flush the ORM before executing raw SQL
        _logger.debug("POLP: Flushing the ORM")
        self.env.cr.flush()

        # Find individuals that have access to this learning program
        _logger.info("POLP: Fetching individual IDs")
        query = """
            SELECT individual_student_id
            FROM individual_polp_access
            WHERE po_learning_program_id = %s AND is_active = %s;
        """
        self._cr.execute(query, (self._origin.id, "true"))
        individual_ids = [row[0] for row in self._cr.fetchall()]
        _logger.info("POLP: Fetched individual IDs completed")
        _logger.debug("POLP: Individual IDs: %s", individual_ids)

        for individual_id in individual_ids:
            _logger.info("POLP: Checking individual %s", individual_id)

            for course_id in new_course_ids:
                _logger.info(
                    "POLP: Checking course access for individual %s and course %s",
                    individual_id,
                    course_id,
                )

                _logger.debug(
                    "POLP: Check if course %s is already part of individual course access",
                    course_id,
                )
                query = """
                    SELECT id, is_active
                    FROM individual_course_access
                    WHERE individual_student_id = %s AND purchased_course_id = %s;
                """
                self._cr.execute(query, (individual_id, course_id))
                result = self._cr.fetchone()
                _logger.debug("POLP: Result: %s", result)

                if result:
                    _logger.info(
                        "POLP: Course %s is already part of individual course access",
                        course_id,
                    )
                    access_id, is_active = result
                    if not is_active:
                        _logger.info(
                            "POLP: Course %s is not active", course_id
                        )
                        update_query = """
                            UPDATE individual_course_access
                            SET is_active = TRUE
                            WHERE id = %s;
                        """
                        self._cr.execute(update_query, (access_id,))
                        _logger.info(
                            "POLP: Set course %s to active", course_id
                        )
                else:
                    _logger.info(
                        "POLP: Course %s is not part of individual course access",
                        course_id,
                    )
                    insert_query = """
                        INSERT INTO individual_course_access (individual_student_id, purchased_course_id, is_single_course, is_active)
                        VALUES (%s, %s, FALSE, TRUE);
                    """
                    self._cr.execute(insert_query, (individual_id, course_id))
                    _logger.info(
                        "POLP: Inserted course %s into individual course access",
                        course_id,
                    )

        self._cr.commit()

    def remove_courses_from_individuals_learning_program(self, old_course_ids):
        _logger.info("POLP: Removing old courses from individuals")
        if not old_course_ids:
            _logger.info("POLP: No old courses to remove")
            return

        _logger.debug("POLP: Flushing the ORM")
        self.env.cr.flush()

        # Find individuals that have access to this learning program
        query = """
            SELECT individual_student_id
            FROM individual_polp_access
            WHERE po_learning_program_id = %s
        """
        self._cr.execute(query, (self._origin.id,))
        individual_ids = [row[0] for row in self._cr.fetchall()]
        _logger.info("POLP: Fetched individual IDs completed")
        _logger.debug("POLP: Individual IDs: %s", individual_ids)

        for individual_id in individual_ids:
            _logger.info("POLP: Checking individual %s", individual_id)
            for course_id in old_course_ids:
                _logger.info(
                    "POLP: Checking course access for individual %s and course %s",
                    individual_id,
                    course_id,
                )

                _logger.debug(
                    "POLP: Check if course %s is in other active learning programs",
                    course_id,
                )
                check_query = """
                    SELECT COUNT(*)
                    FROM individual_polp_access ipa
                    JOIN po_learning_program_course plpc ON ipa.po_learning_program_id = plpc.po_learning_program_ids
                    WHERE ipa.individual_student_id = %s AND plpc.course_ids = %s AND ipa.po_learning_program_id != %s;
                """
                self._cr.execute(
                    check_query, (individual_id, course_id, self._origin.id)
                )
                count = self._cr.fetchone()[0]

                _logger.debug(
                    "POLP: Number of active learning programs with this course: %s",
                    count,
                )

                if count == 0:
                    _logger.info(
                        "POLP: Course %s is not in other active learning programs",
                        course_id,
                    )
                    _logger.debug(
                        "POLP: Check if course %s is purchased separately",
                        course_id,
                    )
                    check_query = """
                        SELECT is_single_course
                        FROM individual_course_access
                        WHERE individual_student_id = %s AND purchased_course_id = %s;
                    """
                    self._cr.execute(check_query, (individual_id, course_id))
                    is_single_course = self._cr.fetchone()[0]
                    _logger.debug(
                        "POLP: Is single course: %s", is_single_course
                    )

                    if not is_single_course:
                        _logger.info(
                            "POLP: Course %s is not purchased separately",
                            course_id,
                        )
                        _logger.debug(
                            "POLP: Setting course %s from individual course access to inactive",
                            course_id,
                        )
                        update_query = """
                            UPDATE individual_course_access
                            SET is_active = FALSE
                            WHERE individual_student_id = %s AND purchased_course_id = %s;
                        """
                        self._cr.execute(
                            update_query, (individual_id, course_id)
                        )

                        _logger.info(
                            "POLP: Set course %s from individual course access to inactive",
                            course_id,
                        )

        self._cr.commit()

    def write(self, vals):
        _logger.info("POLP: Updating PO learning program")
        if "course_list" in vals:
            _logger.info("POLP: Updating course list")
            for record in self:
                current_course_list = record.course_list.ids
                new_course_list = vals["course_list"][0][2]
                _logger.debug(
                    "POLP: Current course list: %s", current_course_list
                )
                _logger.debug("POLP: New course list: %s", new_course_list)

                added_courses = list(
                    set(new_course_list) - set(current_course_list)
                )
                _logger.debug("POLP: Added courses: %s", added_courses)
                removed_courses = list(
                    set(current_course_list) - set(new_course_list)
                )
                _logger.debug("POLP: Removed courses: %s", removed_courses)

                if added_courses:
                    record.add_courses_to_learning_program(added_courses)
                    record.add_courses_to_individuals_learning_program(
                        added_courses
                    )
                    _logger.info(
                        "POLP: Added new courses to PO learning program"
                    )
                if removed_courses:
                    record.remove_courses_from_learning_program(
                        removed_courses
                    )
                    record.remove_courses_from_individuals_learning_program(
                        removed_courses
                    )
                    _logger.info(
                        "POLP: Removed old courses from PO learning program"
                    )

        return super(LearningProgram, self).write(vals)
