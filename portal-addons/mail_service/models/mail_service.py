from odoo import models, api
import sendgrid
from sendgrid.helpers.mail import Mail
import datetime


class MailServiceSendGrid(models.Model):
    _name = "mail_service"

    @api.model
    def send_email_with_sendgrid(
        self, service_key_config, recipient_email, subject, body
    ):
        api_key = service_key_config.get_api_key_by_service_name(
            "Mail Service"
        )

        if api_key:
            try:
                sg = sendgrid.SendGridAPIClient(api_key=api_key)
                from_email = "sendgridtest@email.com"
                to_email = recipient_email
                message = Mail(from_email, to_email, subject, body)
                response = sg.send(message)

                if response.status_code != 202:
                    raise Exception(f"Failed to send email: {response.body}")

                # Write log email
                self.log_sent_email(recipient_email, subject, body)

            except Exception as e:
                # Error when sending email
                print(f"Error sending email: {str(e)}")

    def log_sent_email(self, recipient, subject, body):
        # Create table write log email
        log = self.env["sent_email_log"].create(
            {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "sent_at": datetime.datetime.now(),
            }
        )

        # Save log table
        log.save()
