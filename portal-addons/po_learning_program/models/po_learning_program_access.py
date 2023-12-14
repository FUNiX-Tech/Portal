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
        # print('THIS HAS BEEN CALLED')
        organization_id = vals.get("organization_id")
        # print('organization_id', organization_id)
        po_learning_program_id = vals.get("po_learning_program_id")
        # print('po_learning_program_id', po_learning_program_id)

        # if (self.env['organization_course_access'].search([('student_organization_id', '=', organization_id), ('purchased_course_id', '=', po_learning_program_id)])):
        #     raise UserError('Organization have already purchased this course')

        # Access the course_list using raw SQL
        cr = self._cr

        cr.execute(
            """
                SELECT cm.id
                FROM po_learning_program_course plpc
                JOIN course_management cm ON cm.id = plpc.course_ids
                WHERE plpc.po_learning_program_ids = %s
            """,
            (po_learning_program_id,),
        )

        fetch_result = cr.fetchall()
        # print('FETCH RESULT:', fetch_result)

        course_ids = [row[0] for row in fetch_result]

        cr.execute(
            """SELECT oca.purchased_course_id FROM organization_course_access oca where oca.student_organization_id = %s""",
            (organization_id,),
        )

        purchased_course_ids = [row[0] for row in cr.fetchall()]

        print("purchased_course_ids:", purchased_course_ids)

        try:
            for course_id in course_ids:
                if course_id not in purchased_course_ids:
                    self.env["organization_course_access"].create(
                        {
                            "student_organization_id": organization_id,
                            "purchased_course_id": course_id,
                        }
                    )
            return super(OrgPOLPAccess, self).create(vals)
        except Exception:
            raise UserError("Something went wrong")

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
        # print('THIS HAS BEEN CALLED 2')
        individual_student_id = vals.get("individual_student_id")
        # print('individual_student_id', individual_student_id)
        po_learning_program_id = vals.get("po_learning_program_id")
        # print('po_learning_program_id', po_learning_program_id)

        # if (self.env['individual_course_access'].search([('individual_student_id', '=', individual_student_id), ('purchased_course_id', '=', po_learning_program_id)])):
        #     raise UserError('Student have already purchased this course')

        # Access the course_list using raw SQL
        cr = self._cr

        cr.execute(
            """
                SELECT cm.id
                FROM po_learning_program_course plpc
                JOIN course_management cm ON cm.id = plpc.course_ids
                WHERE plpc.po_learning_program_ids = %s
            """,
            (po_learning_program_id,),
        )

        fetch_result = cr.fetchall()
        course_ids = [row[0] for row in fetch_result]

        cr.execute(
            """SELECT ica.purchased_course_id FROM individual_course_access ica where ica.individual_student_id = %s""",
            (individual_student_id,),
        )

        purchased_course_ids = [row[0] for row in cr.fetchall()]

        # print('purchased_course_ids:', purchased_course_ids)

        try:
            for course_id in course_ids:
                if course_id not in purchased_course_ids:
                    self.env["individual_course_access"].create(
                        {
                            "individual_student_id": individual_student_id,
                            "purchased_course_id": course_id,
                        }
                    )
            return super(IndividualPOLPAccess, self).create(vals)
        except Exception:
            raise UserError("Something went wrong")

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
