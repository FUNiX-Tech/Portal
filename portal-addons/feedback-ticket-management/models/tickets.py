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
    ticket_title = fields.Char(string="Title", required=True)
    ticket_description = fields.Text(string="Ticket Descriptions")
    ticket_attachment = fields.Image(string="Ticket Attachment")
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
                print("bcd", ticket)
                ticket.action_send_mail(ticket.id, "reminder")

    @api.model
    def create(self, vals):
        vals["created_at"] = datetime.now()
        vals["ticket_number"] = (
            self.env["ir.sequence"].sudo().next_by_code("feedback_ticket")
        )
        # if response is submitted to reply requester, the request is done, do like if below to check for api and create on portal.
        if "ticket_response" in vals and vals["ticket_response"]:
            vals["ticket_status"] = "done"
        ticket = super(FeedbackTicket, self).create(vals)
        if (
            "ticket_assignee" in vals
        ):  # If assignee is populated email will be sent to them.
            ticket.action_send_mail(ticket.id)
        if "ticket_response" in vals:
            ticket.action_send_mail(ticket.id, "response")
        return ticket

    def write(self, vals):
        # if response is submitted to reply requester, the request is done
        if "ticket_response" in vals:
            vals["ticket_status"] = "done"
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

    @api.depends("ticket_assignee")
    def _assign_to_you(self):
        for record in self:
            if record.ticket_assignee.id == self.env.user.sudo().id:
                record.assign_to_you = "Assign to you"
            else:
                record.assign_to_you = ""
