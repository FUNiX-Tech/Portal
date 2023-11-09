from odoo import models, fields, api


# Service Key Config
class ServiceKeyConfiguration(models.Model):
    _name = "service_key_configuration"
    _description = "Service Key Configuration"

    name = fields.Char(string="Service Name", required=True)
    api_key = fields.Char(string="API Key", required=True)

    # Method get api key by name of service
    def get_api_key_by_service_name(self, service_name):
        key_record = self.search([("name", "=", service_name)])
        if key_record:
            return key_record.api_key
        else:
            return False
