from odoo import models, fields, api
from datetime import datetime


class StudentGroup(models.Model):
    _name = "student_group"
    _description = "Student Group"

    name = fields.Char(string="name", required=True)
    creator = fields.Char(
        string="creator", default=lambda self: self.env.user.name
    )
    group_note = fields.Text(string="group_note")
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )

    @api.model
    def create(self, vals):
        if "created_at" not in vals:
            vals["created_at"] = datetime.now()
        return super(StudentGroup, self).create(vals)
