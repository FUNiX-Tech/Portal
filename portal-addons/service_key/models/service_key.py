from odoo import models, fields


# Service Key Config
class ServiceKeyConfiguration(models.Model):
    _name = "service_key_configuration"
    _description = "Service Key Configuration"

    name = fields.Char(string="Service Name", required=True)
    key_ids = fields.One2many("service_key", "config_id", string="API Keys")

    # Method get api key by name of service
    def get_api_key_by_service_name(self, service_name):
        key_record = self.key_ids.filtered(
            lambda key: key.name == service_name
        )
        if key_record:
            return key_record.api_key
        else:
            return False


# Service Key
class ServiceKey(models.Model):
    _name = "service_key"
    _description = "Service Key"

    config_id = fields.Many2one(
        "service_key_configuration", string="Service", ondelete="cascade"
    )
    api_key = fields.Char(string="API Key", required=True)
