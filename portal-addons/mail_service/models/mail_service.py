from odoo import models, api, fields
import sendgrid
from sendgrid.helpers.mail import Mail, Content
import datetime


class MailServiceSendGrid(models.AbstractModel):
    _name = "mail_service"
    _description = "Mail Service"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def send_email_with_sendgrid(
        self, service_key_config, recipient_email, subject, body, object
    ):
        api_key = service_key_config.get_api_key_by_service_name(
            "Mail Service"
        )
        if api_key:
            try:
                sg = sendgrid.SendGridAPIClient(api_key=api_key)
                from_email = "no-reply@funix.edu.vn"
                to_email = recipient_email
                message = Mail(
                    from_email, to_email, subject, Content("text/html", body)
                )
                response = sg.send(message)

                if response.status_code != 202:
                    raise Exception(f"Failed to send email: {response.body}")

                # Tạo log chatter
                self.create_chatter_log(object, subject, body, to_email)

            except Exception as e:
                self.create_chatter_log(object, subject, body, to_email, e)

    def create_chatter_log(self, object, subject, body, to_email, e=False):
        # Tạo bản ghi chatter
        if e:
            object.message_post(
                body=f"Email sent to {to_email} with subject '{subject}' has  error {e}"
            )
        else:
            object.message_post(
                body=f"""Email sent to {to_email} with subject '{subject}':
                    {body}""",
            )
