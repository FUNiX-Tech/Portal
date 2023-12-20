from odoo import models, fields, api
from datetime import datetime
import logging
import random

_logger = logging.getLogger(__name__)


class StudentOrganization(models.Model):
    _name = "student_organization"
    _description = "Student Organization"

    name = fields.Char(string="Name", required=True)

    organization_code = fields.Char(string="Organization Code", required=True)

    creator = fields.Char(
        string="Creator", default=lambda self: self.env.user.name
    )
    note = fields.Text(string="Organization Note")
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )

    @api.model
    def create(self, vals):
        _logger.info("Creating student organization")

        if "organization_code" not in vals or not vals["organization_code"]:
            vals["organization_code"] = self._generate_organization_code()

        if "created_at" not in vals:
            vals["created_at"] = datetime.now()

        return super(StudentOrganization, self).create(vals)

    def _generate_organization_code(self):
        while True:
            new_code = str(random.randint(1, 100000)).zfill(6)
            if not self.search([("organization_code", "=", new_code)]):
                return new_code
