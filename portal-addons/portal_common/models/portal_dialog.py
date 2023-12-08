from odoo import models, fields

DIALOG_TYPES = [
    ("warning", "Warning"),
    ("info", "Information"),
    ("error", "Error"),
]
DIALOG_TYPES_DICT = {
    "warning": "Warning",
    "info": "Information",
    "error": "Error",
}


class PortalDialog(models.TransientModel):
    _name = "portal_dialog"
    _description = "Portal Dialog"
    _req_name = "title"

    type = fields.Selection(DIALOG_TYPES, string="Type", readonly=True)
    title = fields.Char(string="Title", readonly=True)
    message = fields.Char(string="Message", readonly=True)

    def post_message(self, type, title, message, context=None):
        created = self.create(
            {"title": title, "message": message, "type": type}
        )

        dialog_name = DIALOG_TYPES_DICT.get(created.type)
        if created.title.strip() != "":
            dialog_name += f": {created.title}"

        res = {
            "name": dialog_name,
            "view_type": "form",
            "view_mode": "form",
            "view_id": self.env.ref(
                "portal_common.portal_dialog_form_view"
            ).id,
            "res_model": "portal_dialog",
            "domain": [],
            "context": context,
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": created.id,
        }

        return res

    def info(self, title, message, context=None):
        return self.post_message("info", title, message, context)

    def error(self, title, message, context=None):
        return self.post_message("error", title, message, context)

    def warning(self, title, message, context=None):
        return self.post_message("warning", title, message, context)
