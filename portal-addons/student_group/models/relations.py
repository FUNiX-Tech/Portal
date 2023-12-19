from odoo import models, fields, api


# Add Student group into student table
class StudentGroup_Student(models.Model):
    _inherit = "portal.student"
    student_group_ids = fields.Many2many(
        comodel_name="student_group",
        relation="business_student_group",
        column1="student_id",
        column2="group_id",
        domain="[('group_organization_id', '=', student_organization_student_ids)]",
    )


class StudentOrganization(models.Model):
    _inherit = "student_organization"

    student_group_ids = fields.One2many(
        comodel_name="student_group",
        inverse_name="group_organization_id",
        string="Group",
    )


class StudentGroup(models.Model):
    _inherit = "student_group"
    business_student_ids = fields.Many2many(
        comodel_name="portal.student",
        relation="business_student_group",
        column1="group_id",
        column2="student_id",
    )

    group_organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Group Organization",
        required=True,
    )

    @api.onchange("group_organization_id")
    def _onchange_group_organization_id(self):
        if self.group_organization_id:
            return {
                "domain": {
                    "business_student_ids": [
                        (
                            "student_organization_student_ids",
                            "=",
                            self.group_organization_id.id,
                        )
                    ]
                }
            }
        else:
            return {"domain": {"business_student_ids": []}}
