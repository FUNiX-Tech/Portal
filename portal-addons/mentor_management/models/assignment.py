from odoo import _, models, fields, api


class Assignment(models.Model):
    _inherit = "assignment"

    assignment_id = fields.Char(
        string="Assignment ID",
        required=True,
        copy=False,
        index=True,
        default=lambda self: _("New"),
    )

    @api.model
    def create(self, vals):
        if vals.get("assignment_id", _("New")) == _("New"):
            vals["assignment_id"] = self.env["ir.sequence"].next_by_code(
                "assignment.assignment"
            ) or _("New")
        result = super(Assignment, self).create(vals)
        return result
