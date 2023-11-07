# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import config


class FeedbackTicket(models.Model):
    _name = "feedback_ticket"
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
    )
    ticket_number = fields.Char(string="Ticket Number", readonly=True)
    ticket_description = fields.Text(string="Ticket Descriptions")
    ticket_attachment = fields.Char(string="Ticket Attachment")
    ticket_assignee = fields.Many2one(
        "res.users",
        string="Assigned Staff",
    )
    assign_to_you = fields.Char(
        compute="_assign_to_you", string="Assign To You"
    )  # field computed to add on information, not store in database

    ticket_requester = fields.Many2one(
        "portal.student", string="Requester"
    )  # Student request a ticket for feedback
    requester_email = fields.Char(
        compute="compute_email_requester", string="Requester Email"
    )
    ticket_response = fields.Text(string="Response")
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
        help="Editable on update view",
    )
    course_rel = fields.Many2one("course_management", string="Course")
    lesson_url = fields.Char(string="Lesson Link")
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
            template.send_mail(ticket_id, force_send=True)
        elif email_type == "response" and self.ticket_requester.email:
            template = self.env.ref(
                "feedback-ticket-management.response_ticket_email_template"
            )
            template.send_mail(ticket_id, force_send=True)
        elif email_type == "reminder":
            template = self.env.ref(
                "feedback-ticket-management.email_assignee_reminder_template"
            )
            datenow = datetime.now()
            template.with_context({"datenow": datenow}).send_mail(
                ticket_id, force_send=True
            )

    # Scheduled send email action as assignee reminder
    def assignee_reminder(self):
        for ticket in self.env["feedback_ticket"].search(
            [("ticket_status", "in", ["assigned", "in_progress"])]
        ):
            if (datetime.now() - ticket.created_at).days % 3 == 0:
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
