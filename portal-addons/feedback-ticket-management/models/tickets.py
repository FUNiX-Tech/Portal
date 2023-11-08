# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class FeedbackTicket(models.Model):
    _name = "feedback_ticket"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "feedback_ticket_management"
    ticket_category = fields.Selection(
        [
            ("outdated", "Content contains outdated information"),
            ("bad_explain", "Content is not explained well"),
            ("insufficient_details", "Content needs more detail"),
            (
                "broken_resource",
                "Resource is missing or broken (link, dataset, etc)",
            ),
            ("error_translation", "Translation Error in content"),
        ],
        string="Ticket Category",
        required=True,
        readonly=True,
    )
    ticket_number = fields.Char(string="Ticket Number", readonly=True)
    ticket_description = fields.Text(
        string="Ticket Descriptions",
        readonly=True,
    )
    ticket_attachment = fields.Char(string="Ticket Attachment", readonly=True)
    ticket_assignee = fields.Many2one(
        "res.users", string="Assigned Staff", tracking=True
    )
    assign_to_you = fields.Char(
        compute="_assign_to_you", string="Assign To You"
    )  # field computed to add on information, not store in database

    ticket_requester = fields.Many2one(
        "portal.student",
        string="Requester",
        readonly=True,
    )  # Student request a ticket for feedback
    requester_email = fields.Char(
        compute="compute_email_requester", string="Requester Email"
    )
    ticket_response = fields.Text(string="Response Content", tracking=True)
    created_at = fields.Datetime(
        string="Created Datetime",
        readonly=True,
        help="Automatically generated",
    )
    ticket_status = fields.Selection(
        [
            ("waiting", "Waiting"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        string="Ticket status",
        required=True,
        default="waiting",
        tracking=True,
    )
    course_rel = fields.Many2one(
        "course_management",
        string="Course",
        readonly=True,
    )
    lesson_url = fields.Char(
        string="Lesson Link",
        readonly=True,
    )
    processing_time = fields.Char(
        string="Processing Time",
        compute="cal_processing_time",
        default="0 days 0 hours",
    )
    complete_date = fields.Datetime(
        string="Complete Ticket Date", readonly=True
    )

    # Action send email based on type
    def action_send_mail(self, ticket_id, email_type="assign"):
        if email_type == "assign" and self.ticket_assignee.email:
            template = self.env.ref(
                "feedback-ticket-management.assign_ticket_email_template"
            )
            email = (
                template.generate_email(
                    ticket_id, fields=["subject", "body_html", "email_to"]
                ),
            )
            self.message_log_email(email)
            template.send_mail(ticket_id, force_send=True)
        elif email_type == "response" and self.ticket_requester.email:
            template = self.env.ref(
                "feedback-ticket-management.response_ticket_email_template"
            )
            email = (
                template.generate_email(
                    ticket_id, fields=["subject", "body_html", "email_to"]
                ),
            )
            self.message_log_email(email)
            template.send_mail(ticket_id, force_send=True)
        elif email_type == "reminder":
            template = self.env.ref(
                "feedback-ticket-management.email_assignee_reminder_template"
            )
            date_diff = (datetime.now() - self.created_at).days
            email = (
                template.with_context({"date_diff": date_diff}).generate_email(
                    ticket_id, fields=["subject", "body_html", "email_to"]
                ),
            )
            self.message_log_email(email)
            template.with_context({"date_diff": date_diff}).send_mail(
                ticket_id, force_send=True
            )

    # Scheduled send email action as assignee reminder
    def assignee_reminder(self):
        for ticket in self.env["feedback_ticket"].search(
            [("ticket_status", "in", ["assigned", "in_progress"])]
        ):
            diff_days = (datetime.now() - ticket.created_at).days
            if diff_days != 0 and diff_days % 3 == 0:
                ticket.action_send_mail(ticket.id, "reminder")

    # Override create method
    @api.model
    def create(self, vals):
        vals["created_at"] = datetime.now()
        vals["ticket_number"] = (
            self.env["ir.sequence"].sudo().next_by_code("feedback_ticket")
        )
        # if response is submitted to reply requester, the request is done, do like if below to check for api and create on portal.
        if "ticket_response" in vals and vals["ticket_response"]:
            vals["ticket_status"] = "done"
            vals["complete_date"] = datetime.now()
        ticket = super(FeedbackTicket, self).create(vals)
        ticket.message_log_create(vals)
        if (
            "ticket_assignee" in vals
        ):  # If assignee is populated email will be sent to them.
            ticket.action_send_mail(ticket.id)
        if "ticket_response" in vals:
            ticket.action_send_mail(ticket.id, "response")
        return ticket

    # Override write method
    def write(self, vals):
        # if response is submitted to reply requester, the request is done
        if "ticket_response" in vals:
            vals["ticket_status"] = "done"
            vals["complete_date"] = datetime.now()
        success = super(FeedbackTicket, self).write(
            vals
        )  # This variable return boolean for update process
        if (
            success and "ticket_assignee" in vals
        ):  # If ticket_assignee is changed (reassign) it will send email again
            self.action_send_mail(self.id)
        if success and "ticket_response" in vals:
            self.action_send_mail(self.id, "response")
        return success

    @api.onchange("ticket_assignee")
    def ticket_assignee_onchange(self):
        if self.ticket_assignee and self.ticket_status == "waiting":
            self.ticket_status = "assigned"

    # Function compute to show "Assign to you" tag if the ticket is assigned to current logged in user.
    @api.depends("ticket_assignee")
    def _assign_to_you(self):
        for record in self:
            if record.ticket_assignee.id == self.env.user.sudo().id:
                record.assign_to_you = "Assign to you"
            else:
                record.assign_to_you = ""

    # Function:
    @api.depends("ticket_requester")
    def compute_email_requester(self):
        for record in self:
            record.requester_email = record.ticket_requester.email

    # Function calculate processing time
    @api.depends("created_at")
    def cal_processing_time(self):
        for ticket in self:
            if ticket.ticket_status in ["waiting", "assigned", "in_progress"]:
                process_time_temp = datetime.now() - ticket.created_at
                ticket.processing_time = f"{process_time_temp.days} days {round(process_time_temp.seconds/3600)} hours"
            elif ticket.ticket_status == "done" and ticket.complete_date:
                process_time_temp = ticket.complete_date - ticket.created_at
                ticket.processing_time = f"{process_time_temp.days} days {round(process_time_temp.seconds/3000)} hours"
            else:
                ticket.processing_time = ""

    # assign datetime now to complete_date when ticket change status to done.
    @api.onchange("ticket_status")
    def ticket_status_change(self):
        if self.ticket_status == "done":
            self.complete_date = datetime.now()
        else:  # reopen ticket complete_date will be none
            self.complete_date = None

    # Tracking message log:
    def message_log_create(self, vals):
        body = "<ul><strong>This ticket has been created:</strong>"
        for field in vals:
            if field == "course_rel":
                value_field = self.course_rel.course_name
            elif field == "ticket_requester":
                value_field = self.ticket_requester.name
            else:
                value_field = vals.get(field)
            body = (
                body + f"<li>{self._fields[field].string}: {value_field}</li>"
            )
        body = body + "</ul>"
        self.message_post(body=body)

    # format body of email and post it to tracing log message
    def message_log_email(self, email_data):
        print("asd")
        body = f"<em>Subject : {email_data[0]['subject']}</em><br/><p>Email to: {email_data[0]['email_to']}</p><br/>{email_data[0]['body_html']}"
        print(body)
        self.message_post(body=body)
