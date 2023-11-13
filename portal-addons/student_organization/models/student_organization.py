from odoo import models, fields, api
from datetime import datetime


class StudentOrganization(models.Model):
    _name = "student_organization"
    _description = "Student Organization"

    name = fields.Char(string="name", required=True)
    creator = fields.Char(
        string="creator", default=lambda self: self.env.user.name
    )
    note = fields.Text(string="note")
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(StudentOrganization, self).create(vals)
