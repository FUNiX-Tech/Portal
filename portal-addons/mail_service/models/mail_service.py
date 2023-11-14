from odoo import models


class MailServiceSendGrid(models.AbstractModel):
    _name = "mail_service"
    _description = "Mail Service"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # func send email
    def send_email_with_sendgrid(
        self,
        service_key_config,
        recipient_email,
        email_cc,
        title,
        subject,
        body,
        description,
        external_link,
        external_text,
        ref_model,
        object,
        email_from,
    ):
        # get api key
        api_key = service_key_config.get_api_key_by_service_name(
            "Mail Service"
        )

        # check api_key
        if api_key:

            def btn_link():
                if external_link and external_text:
                    return f"""<div style="margin-top:1rem;width:100%;text-align:center">
                                        <a style="font-weight:500;text-decoration:none;color:#fff;padding:1rem 0.5rem;background:#875a7b;border-radius:0.25rem;" href="{external_link}">{external_text}</a>
                                    </div>
                                   """
                else:
                    return ""

            # Update the SMTP password XML in ir.mail_server
            mail_server = (
                self.env["ir.mail_server"]
                .sudo()
                .search([("name", "=", "[PORTAL] Outgoing Mail Server")])
            )
            if mail_server:
                mail_server.write({"smtp_pass": api_key})
            template_server = (
                self.env["mail.template"]
                .sudo()
                .search([("name", "=", "[PORTAL] Mail Template")])
            )

            # Update fields in mail template XML
            if template_server:
                # Create body_html content
                body_html = f"""
                        <div style="background:#f1f1f1;width:100%;padding: 2rem 0 0.5rem 0;">
                            <div style="background:#fff;color:#333;max-width:621px;margin: 0 auto;padding: 2rem 2rem 1rem 2rem;box-shadow: 0 0 5px rgba(0,0,0,0.08);">
                                <header style="border-bottom:2px solid #ccc;display:flex;align-items:center;">
                                    <h1 style="width:calc(100% - 5rem);font-size:1.5rem;color:#555;font-weight:500;">{title}</h1>
                                   <div style="width:5rem;display:flex;align-items:center;">
                                        <img alt="funix_mail_logo" style="display:block;width:100%;" src="https://static.ladipage.net/5b1605af9066d9507109d716/220131218_logo-funix-chuan-20220919050027-dszo_.png" />
                                    </div>

                                </header>
                                <main>
                                    {body}
                                    {btn_link()}
                                </main>

                                <footer>
                                <p>Trân trọng,<p/>
                                <p style="font-weight:bold;">FUNiX</p
                                <p><i>Lưu ý: Đây là email gửi tự động, vui lòng không trả lời lại.</i></p>
                                </footer>
                            </div>
                            </div>

                        </div>
                        <p  style="color:#333;margin:0;padding-top:0.5rem;text-align:center">&copy; <a style="color:#875a7b;" href="funix.edu.vn">FUNiX</a> - Learn with mentors</p>
                        </div>
                        """
                mail_ref = self.env.ref(ref_model)
                template_server.write({"subject": subject})
                template_server.write({"email_from": email_from})
                template_server.write({"email_to": recipient_email})
                template_server.write({"body_html": body_html})
                template_server.write({"description": description})
                template_server.write({"email_cc": email_cc})
                template_server.write({"model_id": mail_ref.id})

            # get template send mail
            template = self.env.ref("mail_service.portal_mail_template")

            # send mail action
            template.send_mail(object.id, force_send=True)
            # write log mail message
            object.message_post(
                body=f"Email sent to {recipient_email} with subject '{subject}' and content \n '{body}' "
            )
