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
    check_group = fields.Boolean(
        string="Check Group Super User",
        compute="_compute_check_group",
        default=True,
    )  # If user not included in group super user, field name and private will be read-only

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
            if (
                record.name
                and self.search_count([("name", "=", record.name)]) > 1
            ):
                raise exceptions.ValidationError(
                    "Already exists, name must be unique!"
                )
            if record.name and re.search(r"[^A-Z0-9_]", record.name):
                raise exceptions.ValidationError(
                    "All letters in the name must be uppercase and it cannot contain special characters, except underscore (_)"
                )
            if re.search(r"\_{2,}", record.name):
                raise exceptions.ValidationError(
                    "Only one undrscore (_) is allowed between words!"
                )

    def check_key_existing(self, key_name):
        key = self.search([("name", "=", key_name)])
        if key:
            return True
        else:
            return False

    @api.model
    def set_default_key(self):
        key_lists = [
            {
                "name": "LMS_BASE",
                "api_key": "https://test-xseries.funix.edu.vn/",
                "private": False,
            },
            {"name": "SLA_TICKET_REMINDER_TIME_IN_DAY", "api_key": 3},
            {"name": "SLA_MENTOR_REMINDER_TIME_IN_DAY", "api_key": 3},
            {
                "name": "MAIL_SERVICE",
                "api_key": "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",
            },
            {
                "name": "API_BULK_ENROLL",
                "api_key": "api/bulk_enroll/v1/bulk_enroll",
            },
            {"name": "MIGRATE_CHECK", "api_key": "False"},
            {"name": "UDEMY_BASE", "api_key": "https://24d1-14-161-31-73.ngrok-free.app/"}
        ]
        for key in key_lists:
            if not self.check_key_existing(key["name"]):  # if key not existing
                if key.get("private"):
                    super(ServiceKeyConfiguration, self).create(
                        {
                            "name": key.get("name"),
                            "private": True,
                            "_original_api_key": key.get("api_key"),
                        }
                    )
                else:
                    super(ServiceKeyConfiguration, self).create(
                        key | {"private": False}
                    )

    @api.depends_context("uid")
    def _compute_check_group(self):
        self.check_group = self.env.user.has_group(
            "service_key.group_service_key_super_user"
        )
