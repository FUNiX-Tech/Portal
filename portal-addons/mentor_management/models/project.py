from odoo import _, models, fields, api


class Project(models.Model):
    _inherit = "project"

    project_id = fields.Char(
        string="Project ID",
        required=True,
        copy=False,
        index=True,
        default=lambda self: _("New"),
    )

    @api.model
    def create(self, vals):
        if vals.get("project_id", _("New")) == _("New"):
            vals["project_id"] = self.env["ir.sequence"].next_by_code(
                "learning_project.project"
            ) or _("New")
        result = super(Project, self).create(vals)
        return result
