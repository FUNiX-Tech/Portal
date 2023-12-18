from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OrgPOLPAccess(models.Model):
    _name = "organization_polp_access"
    _description = "Organization PO Learning Program Access"

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    po_learning_program_id = fields.Many2one(
        comodel_name="po_learning_program",
        string="PO Learning Program",
        required=True,
    )

    is_active = fields.Boolean(
        string="Is Active",
        default=True,
    )

    def write(self, vals):
        self.ensure_one()
        print("SELF.ENSURE ONE", self.ensure_one())
        print("POLP: organization_idDDD", self.organization_id.id)
        print(
            "POLP:po_learning_program_idDDDD",
            self.po_learning_program_id.course_list.ids,
        )
        _logger.info(
            "POLP: Updating Learning Program access record for organization"
        )

        cousre_access_env = self.env["organization_course_access"]

        if "is_active" in vals:
            if vals.get("is_active"):
                _logger.info("POLP: Activating access record")
                for course_id in self.po_learning_program_id.course_list.ids:
                    self.env["organization_course_access"].search(
                        [
                            (
                                "student_organization_id",
                                "=",
                                self.organization_id.id,
                            ),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write(
                        {
                            "is_active": True,
                        }
                    )
                    _logger.info("POLP: Access record activated")
            else:
                _logger.info("POLP: Deactivating access record")
                self._deactivate_course_access(
                    self,
                    self.organization_id.id,
                    self.po_learning_program_id.id,
                    cousre_access_env,
                )

        return super().write(vals)

    @api.model
    def create(self, vals):
        _logger.info("POLP: Creating new access record for organization")
        organization_id = vals.get("organization_id")
        po_learning_program_id = vals.get("po_learning_program_id")

        _logger.debug("POLP: Organization ID: %s", organization_id)
        _logger.debug(
            "POLP: PO Learning Program ID: %s", po_learning_program_id
        )

        cr = self._cr

        # Fetch course IDs from the new learning program
        _logger.info("POLP: Fetching new course IDs")
        cr.execute(
            """
                SELECT cm.id
                FROM po_learning_program_course plpc
                JOIN course_management cm ON cm.id = plpc.course_ids
                WHERE plpc.po_learning_program_ids = %s
            """,
            (po_learning_program_id,),
        )
        new_course_ids = [row[0] for row in cr.fetchall()]
        _logger.info("POLP: Fetched new course IDs completed")
        _logger.debug("POLP: New course IDs: %s", new_course_ids)

        # Fetch existing course access records for the organization
        _logger.info("POLP: Fetching existing course access records")

        cr.execute(
            """SELECT oca.purchased_course_id, oca.is_active
               FROM organization_course_access oca
               WHERE oca.student_organization_id = %s""",
            (organization_id,),
        )
        existing_course_access = {row[0]: row[1] for row in cr.fetchall()}
        _logger.info("POLP: Fetched existing course access records completed")
        _logger.debug(
            "POLP: Existing course access records: %s", existing_course_access
        )

        _logger.info("POLP: Creating new course access records")
        try:
            for course_id in new_course_ids:
                _logger.info(
                    "POLP: Creating new course access record for course ID %s",
                    course_id,
                )
                _logger.debug(
                    "Checking if course %s is already accessed by organization",
                    course_id,
                )
                is_active = existing_course_access.get(course_id)
                _logger.debug("Course %s is active: %s", course_id, is_active)
                if course_id not in existing_course_access:
                    _logger.info(
                        "Course %s is not  accessed by organization", course_id
                    )
                    # Course not accessed before, create new access
                    _logger.info(
                        "Creating new course access record for course ID %s",
                        course_id,
                    )
                    self.env["organization_course_access"].create(
                        {
                            "student_organization_id": organization_id,
                            "purchased_course_id": course_id,
                            "is_single_course": False,
                            "is_active": True,
                        }
                    )
                    _logger.info(
                        "Created new course access record for course ID %s",
                        course_id,
                    )
                elif is_active is False:
                    # Course previously accessed but inactive, reactivate it
                    _logger.info("Reactivating course %s", course_id)
                    self.env["organization_course_access"].search(
                        [
                            ("student_organization_id", "=", organization_id),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": True})
                    _logger.info("Reactivated course %s", course_id)

            return super(OrgPOLPAccess, self).create(vals)
        except Exception as e:
            _logger.error("POLP: An error occurred: %s", e)
            raise UserError("An error occurred: %s" % e)

    @api.onchange("organization_id")
    def _onchange_organization_id(self):
        _logger.info("POLP: Changing organization ID")
        if not self.organization_id:
            _logger.info("POLP: Organization ID not set")
            return

        _logger.info("POLP: Organization ID set")
        _logger.info("POLP: Fetching available PO learning programs")
        already_accessed_ids = (
            self.env["organization_polp_access"]
            .search([("organization_id", "=", self.organization_id.id)])
            .mapped("po_learning_program_id.id")
        )

        _logger.info(
            "POLP: Available PO learning programs fetched successfully"
        )
        _logger.debug("POLP: Already accessed IDs: %s", already_accessed_ids)
        return {
            "domain": {
                "po_learning_program_id": [
                    ("id", "not in", already_accessed_ids)
                ]
            }
        }

    def _deactivate_course_access(
        self,
        record,
        org_id,
        po_learning_program_id,
        course_access_env,
        use_active_flag=True,
    ):
        for course_id in record.po_learning_program_id.course_list.ids:
            # Check if this course is in other active learning programs
            _logger.info(
                "POLP: Checking if course %s is in other active learning programs",
                course_id,
            )
            other_programs = self.env["organization_polp_access"].search(
                [
                    ("organization_id", "=", org_id),
                    (
                        "po_learning_program_id",
                        "!=",
                        po_learning_program_id,
                    ),
                    (
                        "po_learning_program_id.course_list",
                        "in",
                        [course_id],
                    ),
                ]
            )
            _logger.info(
                "POLP: Other active learning programs: %s", other_programs
            )

            if not other_programs:
                _logger.info(
                    "POLP: Course is not in other active learning programs, Deactivating course %s",
                    course_id,
                )
                course_access_env.search(
                    [
                        ("student_organization_id", "=", org_id),
                        ("purchased_course_id", "=", course_id),
                    ]
                ).write({"is_active": False})
                _logger.info("POLP: Deactivated course %s", course_id)

            if other_programs and use_active_flag:
                _logger.info(
                    "POLP: Check if course %s is in other ACTIVE learning programs",
                    course_id,
                )
                other_active_programs = other_programs.filtered(
                    lambda r: r.is_active
                )
                _logger.info(
                    "POLP: Other ACTIVE learning programs: %s",
                    other_active_programs,
                )
                if not other_active_programs:
                    _logger.info(
                        "POLP: Course is not in other active learning programs, Deactivating course %s",
                        course_id,
                    )
                    course_access_env.search(
                        [
                            ("student_organization_id", "=", org_id),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": False})
                    _logger.info("POLP: Deactivated course %s", course_id)

    def unlink(self):
        _logger.info("POLP: Deleting course access records for organization")
        course_access_env = self.env["organization_course_access"]
        _logger.debug("POLP: Course access environment: %s", course_access_env)
        for record in self:
            _logger.info("POLP: Deleting course access records")
            org_id = record.organization_id.id
            po_learning_program_id = record.po_learning_program_id.id
            _logger.info(
                "POLP: Deleting course access records for organization %s and PO learning program %s",
                org_id,
                po_learning_program_id,
            )

            self._deactivate_course_access(
                record,
                org_id,
                po_learning_program_id,
                course_access_env,
                use_active_flag=False,
            )

        _logger.info("POLP: Course access records deleted successfully")
        return super(OrgPOLPAccess, self).unlink()


class IndividualPOLPAccess(models.Model):
    _name = "individual_polp_access"
    _description = "Individual PO Learning Program Access"

    individual_student_id = fields.Many2one(
        comodel_name="portal.student",
        string="Individual Student",
        required=True,
        domain="[('student_organization_student_ids', '=', False)]",
    )

    po_learning_program_id = fields.Many2one(
        comodel_name="po_learning_program",
        string="PO Learning Program",
        required=True,
    )

    is_active = fields.Boolean(string="Is Active", default=True)

    @api.model
    def create(self, vals):
        _logger.info("POLP: Creating new access record for individual student")
        individual_student_id = vals.get("individual_student_id")
        po_learning_program_id = vals.get("po_learning_program_id")

        _logger.debug("POLP: Individual Student ID: %s", individual_student_id)
        _logger.debug(
            "POLP: PO Learning Program ID: %s", po_learning_program_id
        )

        cr = self._cr

        # Fetch course IDs from the new learning program
        _logger.info("POLP: Fetching new course IDs")
        cr.execute(
            """
                SELECT cm.id
                FROM po_learning_program_course plpc
                JOIN course_management cm ON cm.id = plpc.course_ids
                WHERE plpc.po_learning_program_ids = %s
            """,
            (po_learning_program_id,),
        )
        new_course_ids = [row[0] for row in cr.fetchall()]
        _logger.info("POLP: Fetched new course IDs completed")
        _logger.debug("POLP: New course IDs: %s", new_course_ids)

        # Fetch existing course access records for the individual student
        _logger.info("POLP: Fetching existing course access records")
        cr.execute(
            """SELECT ica.purchased_course_id, ica.is_active
               FROM individual_course_access ica
               WHERE ica.individual_student_id = %s""",
            (individual_student_id,),
        )
        existing_course_access = {row[0]: row[1] for row in cr.fetchall()}
        _logger.info("POLP: Fetched existing course access records completed")
        _logger.debug(
            "POLP: Existing course access records: %s", existing_course_access
        )

        _logger.info("POLP: Creating new course access records")
        try:
            for course_id in new_course_ids:
                _logger.info(
                    "POLP: Creating new course access record for course ID %s",
                    course_id,
                )
                _logger.debug(
                    "Checking if course %s is already accessed by individual",
                    course_id,
                )
                is_active = existing_course_access.get(course_id)
                _logger.debug("Course %s is active: %s", course_id, is_active)
                if course_id not in existing_course_access:
                    _logger.info(
                        "Course %s is not  accessed by individual", course_id
                    )
                    # Course not accessed before, create new access
                    _logger.info(
                        "Creating new course access record for course ID %s",
                        course_id,
                    )
                    self.env["individual_course_access"].create(
                        {
                            "individual_student_id": individual_student_id,
                            "purchased_course_id": course_id,
                            "is_single_course": False,
                            "is_active": True,
                        }
                    )
                    _logger.info(
                        "Created new course access record for course ID %s",
                        course_id,
                    )
                elif is_active is False:
                    # Course previously accessed but inactive, reactivate it
                    _logger.info("Reactivating course %s", course_id)
                    self.env["individual_course_access"].search(
                        [
                            (
                                "individual_student_id",
                                "=",
                                individual_student_id,
                            ),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": True})
                    _logger.info("Reactivated course %s", course_id)

            return super(IndividualPOLPAccess, self).create(vals)
        except Exception as e:
            _logger.error("POLP: An error occurred: %s", e)
            raise UserError("An error occurred: %s" % e)

    @api.onchange("individual_student_id")
    def _onchange_individual_student_id(self):
        _logger.info("POLP: Onchange event for individual student ID")
        if not self.individual_student_id:
            _logger.info("POLP: Individual student ID not set")
            return

        _logger.info("POLP: Individual student ID set")
        _logger.info("POLP: Fetching available PO learning programs")
        already_purchased_ids = (
            self.env["individual_polp_access"]
            .search(
                [("individual_student_id", "=", self.individual_student_id.id)]
            )
            .mapped("po_learning_program_id.id")
        )

        _logger.info(
            "POLP: Available PO learning programs fetched successfully"
        )
        _logger.debug("POLP: Already purchased IDs: %s", already_purchased_ids)
        return {
            "domain": {
                "po_learning_program_id": [
                    ("id", "not in", already_purchased_ids)
                ]
            }
        }

    def _deactivate_course_access(
        self,
        record,
        individual_id,
        po_learning_program_id,
        course_access_env,
        use_active_flag=True,
    ):
        for course_id in record.po_learning_program_id.course_list.ids:
            # Check if this course is in other active learning programs
            _logger.info(
                "POLP: Checking if course %s is in other active learning programs",
                course_id,
            )
            other_programs = self.env["individual_polp_access"].search(
                [
                    ("individual_student_id", "=", individual_id),
                    (
                        "po_learning_program_id",
                        "!=",
                        po_learning_program_id,
                    ),
                    (
                        "po_learning_program_id.course_list",
                        "in",
                        [course_id],
                    ),
                ]
            )
            _logger.info(
                "POLP: Other active learning programs: %s", other_programs
            )

            if not other_programs:
                _logger.info(
                    "POLP: Course is not in other active learning programs, Deactivating course %s",
                    course_id,
                )
                course_access_env.search(
                    [
                        ("individual_student_id", "=", individual_id),
                        ("purchased_course_id", "=", course_id),
                    ]
                ).write({"is_active": False})
                _logger.info("POLP: Deactivated course %s", course_id)

            if other_programs and use_active_flag:
                _logger.info(
                    "POLP: Check if course %s is in other ACTIVE learning programs",
                    course_id,
                )
                other_active_programs = other_programs.filtered(
                    lambda r: r.is_active
                )
                _logger.info(
                    "POLP: Other ACTIVE learning programs: %s",
                    other_active_programs,
                )
                if not other_active_programs:
                    _logger.info(
                        "POLP: Course is not in other active learning programs, Deactivating course %s",
                        course_id,
                    )

                    course_access_env.search(
                        [
                            ("individual_student_id", "=", individual_id),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": False})
                    _logger.info("POLP: Deactivated course %s", course_id)

    def write(self, vals):
        self.ensure_one()
        print("POLP: individual_student_idDDDD", self.individual_student_id.id)
        print(
            "POLP:po_learning_program_idDDDD",
            self.po_learning_program_id.course_list.ids,
        )

        _logger.info(
            "POLP: Updating Learning Program access record for individual"
        )

        course_access_env = self.env["individual_course_access"]

        if "is_active" in vals:
            if vals.get("is_active"):
                _logger.info("POLP: Activating access record")
                for course_id in self.po_learning_program_id.course_list.ids:
                    self.env["individual_course_access"].search(
                        [
                            (
                                "individual_student_id",
                                "=",
                                self.individual_student_id.id,
                            ),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": True})
                    _logger.info("POLP: Access record activated")

            else:
                _logger.info("POLP: Deactivating access record")
                self._deactivate_course_access(
                    self,
                    self.individual_student_id.id,
                    self.po_learning_program_id.id,
                    course_access_env,
                )
                _logger.info("POLP: Access record deactivated")

        return super(IndividualPOLPAccess, self).write(vals)

    def unlink(self):
        _logger.info(
            "POLP: Deleting course access records for individual student"
        )
        course_access_env = self.env["individual_course_access"]
        _logger.debug("POLP: Course access environment: %s", course_access_env)
        for record in self:
            _logger.info("POLP: Deleting course access records")
            individual_id = record.individual_student_id.id
            po_learning_program_id = record.po_learning_program_id.id
            _logger.info(
                "POLP: Deleting course access records for individual %s and PO learning program %s",
                individual_id,
                po_learning_program_id,
            )

            self._deactivate_course_access(
                record,
                individual_id,
                po_learning_program_id,
                course_access_env,
                use_active_flag=False,
            )

        _logger.info("POLP: Course access records deleted successfully")
        return super(IndividualPOLPAccess, self).unlink()
