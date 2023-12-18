from odoo import models, fields, api
from odoo.exceptions import UserError


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

    @api.model
    def create(self, vals):
        organization_id = vals.get("organization_id")
        po_learning_program_id = vals.get("po_learning_program_id")

        cr = self._cr

        # Fetch course IDs from the new learning program
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

        # Fetch existing course access records for the organization
        cr.execute(
            """SELECT oca.purchased_course_id, oca.is_active
               FROM organization_course_access oca
               WHERE oca.student_organization_id = %s""",
            (organization_id,),
        )
        existing_course_access = {row[0]: row[1] for row in cr.fetchall()}

        print("EXISTING COURSE ACCESS", existing_course_access)

        try:
            for course_id in new_course_ids:
                is_active = existing_course_access.get(course_id)
                if course_id not in existing_course_access:
                    # Course not accessed before, create new access
                    self.env["organization_course_access"].create(
                        {
                            "student_organization_id": organization_id,
                            "purchased_course_id": course_id,
                            "is_single_course": False,
                            "is_active": True,
                        }
                    )
                elif is_active is False:
                    # Course previously accessed but inactive, reactivate it
                    self.env["organization_course_access"].search(
                        [
                            ("student_organization_id", "=", organization_id),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": True})

            return super(OrgPOLPAccess, self).create(vals)
        except Exception as e:
            raise UserError("An error occurred: %s" % e)

    @api.onchange("organization_id")
    def _onchange_organization_id(self):
        if not self.organization_id:
            return

        already_accessed_ids = (
            self.env["organization_polp_access"]
            .search([("organization_id", "=", self.organization_id.id)])
            .mapped("po_learning_program_id.id")
        )

        return {
            "domain": {
                "po_learning_program_id": [
                    ("id", "not in", already_accessed_ids)
                ]
            }
        }

    def unlink(self):
        course_access_env = self.env["organization_course_access"]
        for record in self:
            org_id = record.organization_id.id
            learning_program_id = record.po_learning_program_id.id

            for course_id in record.po_learning_program_id.course_list.ids:
                # Check if this course is in other active learning programs
                other_programs = self.env["organization_polp_access"].search(
                    [
                        ("organization_id", "=", org_id),
                        ("po_learning_program_id", "!=", learning_program_id),
                        (
                            "po_learning_program_id.course_list",
                            "in",
                            [course_id],
                        ),
                    ]
                )

                if not other_programs:
                    # Deactivate the course as it's not in other active programs
                    course_access_env.search(
                        [
                            ("student_organization_id", "=", org_id),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": False})

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

    @api.model
    def create(self, vals):
        individual_student_id = vals.get("individual_student_id")
        po_learning_program_id = vals.get("po_learning_program_id")

        cr = self._cr

        # Fetch course IDs from the new learning program
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

        # Fetch existing course access records for the individual student
        cr.execute(
            """SELECT ica.purchased_course_id, ica.is_active
               FROM individual_course_access ica
               WHERE ica.individual_student_id = %s""",
            (individual_student_id,),
        )
        existing_course_access = {row[0]: row[1] for row in cr.fetchall()}

        try:
            for course_id in new_course_ids:
                is_active = existing_course_access.get(course_id)
                if course_id not in existing_course_access:
                    # Course not accessed before, create new access
                    self.env["individual_course_access"].create(
                        {
                            "individual_student_id": individual_student_id,
                            "purchased_course_id": course_id,
                            "is_single_course": False,
                            "is_active": True,
                        }
                    )
                elif is_active is False:
                    # Course previously accessed but inactive, reactivate it
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

            return super(IndividualPOLPAccess, self).create(vals)
        except Exception as e:
            raise UserError("An error occurred: %s" % e)

    @api.onchange("individual_student_id")
    def _onchange_individual_student_id(self):
        if not self.individual_student_id:
            return

        already_purchased_ids = (
            self.env["individual_polp_access"]
            .search(
                [("individual_student_id", "=", self.individual_student_id.id)]
            )
            .mapped("po_learning_program_id.id")
        )

        return {
            "domain": {
                "po_learning_program_id": [
                    ("id", "not in", already_purchased_ids)
                ]
            }
        }

    def unlink(self):
        course_access_env = self.env["individual_course_access"]
        for record in self:
            individual_id = record.individual_student_id.id
            learning_program_id = record.po_learning_program_id.id

            for course_id in record.po_learning_program_id.course_list.ids:
                # Check if this course is in other active learning programs
                other_programs = self.env["individual_polp_access"].search(
                    [
                        ("individual_student_id", "=", individual_id),
                        ("po_learning_program_id", "!=", learning_program_id),
                        (
                            "po_learning_program_id.course_list",
                            "in",
                            [course_id],
                        ),
                    ]
                )

                if not other_programs:
                    # Deactivate the course as it's not in other active programs
                    course_access_env.search(
                        [
                            ("individual_student_id", "=", individual_id),
                            ("purchased_course_id", "=", course_id),
                        ]
                    ).write({"is_active": False})

        return super(IndividualPOLPAccess, self).unlink()
