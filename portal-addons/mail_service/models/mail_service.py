from odoo import models, api, fields
import sendgrid
from sendgrid.helpers.mail import Mail, Content
import datetime


class MailServiceSendGrid(models.TransientModel):
    _name = "mail_service"
    _description = "Mail Service"

    # send mail func
    def send_email_with_sendgrid(
        self, service_key_config, recipient_email, subject, body
    ):
        # Get api key from service_key module
        api_key = service_key_config.get_api_key_by_service_name(
            "Mail Service"
        )

        # Check api_key exist
        if api_key:
            try:
                # setup sendgrid
                sg = sendgrid.SendGridAPIClient(api_key=api_key)
                from_email = "no-reply@funix.edu.vn"
                to_email = recipient_email
                message = Mail(
                    from_email, to_email, subject, Content("text/html", body)
                )
                response = sg.send(message)

                # Sending mail failed
                if response.status_code != 202:
                    raise Exception(f"Failed to send email: {response.body}")

                # Write log email
                # self.log_sent_email(recipient_email, subject, body)

            except Exception as e:
                # Error when sending email
                print(f"Error sending email: {str(e)}")
        else:
            print("API Key not found for Mail Service")
            return False
