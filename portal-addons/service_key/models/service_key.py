from odoo import models, fields, api, exceptions
import re


# Service Key Config
class ServiceKeyConfiguration(models.Model):
    _name = "service_key_configuration"
    _description = "Setting Config"

    name = fields.Char(string="Setting Name", required=True, unique=True)
    api_key = fields.Char(string="Setting Value", default="")
    private = fields.Boolean(string="Private")
    _original_api_key = fields.Char(string="Original API Key")

    # Method get api key by name of service
    def get_api_key_by_service_name(self, service_name):
        key_record = self.search([("name", "=", service_name)])
        if key_record.api_key:
            return key_record.api_key
        if key_record._original_api_key:
            return key_record._original_api_key
        return False

    # when private change
    @api.onchange("private")
    def _onchange_private(self):
        if self.private and self.api_key:
            # Save the original value of api_key
            self._original_api_key = self.api_key
            # Set api_key to an empty string
            self.api_key = ""
        if not self.private and not self.api_key:
            # Restore the original value of api_key
            self.api_key = self._original_api_key
            self._original_api_key = ""

    # When craete a new setting
    @api.model
    def create(self, values):
        # Check if the 'private' field is changed and set api_key accordingly
        if "private" not in values and values["private"]:
            values["_original_api_key"] = values["api_key"]
            values["api_key"] = ""
        return super(ServiceKeyConfiguration, self).create(values)

    # When edit/update
    def write(self, values):
        if (
            "private" not in values
            and self.private
            and "api_key" in values
            and values["api_key"]
        ):
            values["_original_api_key"] = values["api_key"]
            values["api_key"] = ""

        if (
            "private" in values
            and "_original_api_key" in values
            and "api_key" in values
            and ["private"]
            and values["_original_api_key"]
            and values["api_key"]
        ):
            values["_original_api_key"] = values["api_key"]
            values["api_key"] = ""

        return super(ServiceKeyConfiguration, self).write(values)

    # Name of key validation
    @api.constrains("name")
    def _check_name_length(self):
        for record in self:
            if record.name and len(record.name) < 6:
                raise exceptions.ValidationError(
                    "Name must be at least 6 characters long!"
                )
            if (
                record.name
                and self.search_count([("name", "=", record.name)]) > 1
            ):
                raise exceptions.ValidationError(
                    "Already exists, name must be unique!"
                )
            if record.name and re.search(r"[^a-zA-Z0-9\s]", record.name):
                raise exceptions.ValidationError(
                    "Name cannot contain special characters, except space letters!"
                )
            if not record.name[0].isupper() or re.search(
                r"\s([a-z])", record.name
            ):
                raise exceptions.ValidationError(
                    "The first letter of a word must be uppercase!"
                )
            if re.search(r"\s{2,}", record.name):
                raise exceptions.ValidationError(
                    "Only one space is allowed between words!"
                )
