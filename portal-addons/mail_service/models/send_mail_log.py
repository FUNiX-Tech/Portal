from odoo import models, fields


class SentEmailLog(models.Model):
    _name = "sent_email_log"
    _description = "Sent Email Log"

    recipient = fields.Char(string="Recipient", required=True)
    subject = fields.Char(string="Subject")
    body = fields.Text(string="Body")
    sent_at = fields.Datetime(string="Sent At")
