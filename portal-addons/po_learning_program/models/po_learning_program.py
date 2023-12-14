from odoo import models, fields, api

from datetime import datetime


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
    # !TODO: Change creator to res.user
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
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(LearningProgram, self).create(vals)

    @api.depends("course_list")
    def _compute_old_course_list(self):
        for record in self:
            if record._origin.course_list:
                record.old_course_list = record._origin.course_list
            else:
                record.old_course_list = []

    def add_courses_to_learning_program(self, new_course_ids):
        if not new_course_ids:
            return

        if not self._origin.id:
            print("self._origin.id in if", self._origin.id)
            return
        # Before executing raw SQL, flush the ORM to ensure data consistency
        self.env.cr.flush()
        print("THIS HAS BEEN CALLEDAAAAAAAAAAAAAAAAA")
        print("self._origin.id", self._origin.id)
        # Current po learning program id

        # Find organizations that have access to this learning program
        query = """
            SELECT organization_id
            FROM organization_polp_access
            WHERE po_learning_program_id = %s
        """
        self._cr.execute(query, (self._origin.id,))
        organization_ids = [row[0] for row in self._cr.fetchall()]

        for org_id in organization_ids:
            # Check and update existing course access or add new access
            for course_id in new_course_ids:
                query = """
                    SELECT id, is_active
                    FROM organization_course_access
                    WHERE student_organization_id = %s AND purchased_course_id = %s;
                """
                self._cr.execute(query, (org_id, course_id))
                result = self._cr.fetchone()

                if result:
                    access_id, is_active = result
                    if not is_active:
                        # Reactivate the inactive course
                        update_query = """
                            UPDATE organization_course_access
                            SET is_active = TRUE
                            WHERE id = %s;
                        """
                        self._cr.execute(update_query, (access_id,))
                else:
                    # Insert new course access
                    insert_query = """
                        INSERT INTO organization_course_access (student_organization_id, purchased_course_id, is_single_course, is_active)
                        VALUES (%s, %s, FALSE, TRUE);
                    """
                    self._cr.execute(insert_query, (org_id, course_id))

        self._cr.commit()

    def remove_courses_from_learning_program(self, old_course_ids):
        if not old_course_ids:
            return

        # Flush the ORM before executing raw SQL
        # self.env.cr.flush()

        # Find organizations that have access to this learning program
        query = """
            SELECT organization_id
            FROM organization_polp_access
            WHERE po_learning_program_id = %s
        """
        self._cr.execute(query, (self._origin.id,))
        organization_ids = [row[0] for row in self._cr.fetchall()]

        for org_id in organization_ids:
            for course_id in old_course_ids:
                # Check if the course is part of other learning programs
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

                if count == 0:
                    # Check if the course is purchased separately
                    check_query = """
                        SELECT is_single_course
                        FROM organization_course_access
                        WHERE student_organization_id = %s AND purchased_course_id = %s;
                    """
                    self._cr.execute(check_query, (org_id, course_id))
                    is_single_course = self._cr.fetchone()[0]

                    if not is_single_course:
                        # Set course to inactive
                        update_query = """
                            UPDATE organization_course_access
                            SET is_active = FALSE
                            WHERE student_organization_id = %s AND purchased_course_id = %s;
                        """
                        self._cr.execute(update_query, (org_id, course_id))

        self._cr.commit()

    def add_courses_to_individuals_learning_program(self, new_course_ids):
        if not new_course_ids:
            return

        if not self._origin.id:
            return

        # Flush the ORM before executing raw SQL
        self.env.cr.flush()

        # Find individuals that have access to this learning program
        query = """
            SELECT individual_student_id
            FROM individual_polp_access
            WHERE po_learning_program_id = %s
        """
        self._cr.execute(query, (self._origin.id,))
        individual_ids = [row[0] for row in self._cr.fetchall()]

        for individual_id in individual_ids:
            for course_id in new_course_ids:
                query = """
                    SELECT id, is_active
                    FROM individual_course_access
                    WHERE individual_student_id = %s AND purchased_course_id = %s;
                """
                self._cr.execute(query, (individual_id, course_id))
                result = self._cr.fetchone()

                if result:
                    access_id, is_active = result
                    if not is_active:
                        update_query = """
                            UPDATE individual_course_access
                            SET is_active = TRUE
                            WHERE id = %s;
                        """
                        self._cr.execute(update_query, (access_id,))
                else:
                    insert_query = """
                        INSERT INTO individual_course_access (individual_student_id, purchased_course_id, is_single_course, is_active)
                        VALUES (%s, %s, FALSE, TRUE);
                    """
                    self._cr.execute(insert_query, (individual_id, course_id))

        self._cr.commit()

    def remove_courses_from_individuals_learning_program(self, old_course_ids):
        if not old_course_ids:
            return

        self.env.cr.flush()

        query = """
            SELECT individual_student_id
            FROM individual_polp_access
            WHERE po_learning_program_id = %s
        """
        self._cr.execute(query, (self._origin.id,))
        individual_ids = [row[0] for row in self._cr.fetchall()]

        for individual_id in individual_ids:
            for course_id in old_course_ids:
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

                if count == 0:
                    check_query = """
                        SELECT is_single_course
                        FROM individual_course_access
                        WHERE individual_student_id = %s AND purchased_course_id = %s;
                    """
                    self._cr.execute(check_query, (individual_id, course_id))
                    is_single_course = self._cr.fetchone()[0]

                    if not is_single_course:
                        update_query = """
                            UPDATE individual_course_access
                            SET is_active = FALSE
                            WHERE individual_student_id = %s AND purchased_course_id = %s;
                        """
                        self._cr.execute(
                            update_query, (individual_id, course_id)
                        )

        self._cr.commit()

    def write(self, vals):
        if "course_list" in vals:
            for record in self:
                current_course_list = record.course_list.ids
                new_course_list = vals["course_list"][0][2]

                added_courses = list(
                    set(new_course_list) - set(current_course_list)
                )
                removed_courses = list(
                    set(current_course_list) - set(new_course_list)
                )

                if added_courses:
                    record.add_courses_to_learning_program(added_courses)
                    record.add_courses_to_individuals_learning_program(
                        added_courses
                    )

                if removed_courses:
                    record.remove_courses_from_learning_program(
                        removed_courses
                    )
                    record.remove_courses_from_individuals_learning_program(
                        removed_courses
                    )

        return super(LearningProgram, self).write(vals)
