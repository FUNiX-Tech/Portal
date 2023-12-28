# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Mentor(models.Model):
    _name = "mentor_management"
    _description = "Mentor Management"
    _rec_name = "email"

    full_name = fields.Char(string="Fullname", required=True)
    mentor_code = fields.Char(string="Mentor Code", required=True)
    email = fields.Char(string="Email")
    active_courses = fields.Many2many(
        "course_management",
        relation="mentor_course_table",
        column1="mentor_ids",
        column2="course_ids",
        string="Courses active for mentor",
    )
    submission_ids = fields.One2many(
        "project_submission", "mentor_id", string="Submissions"
    )
    create_date = fields.Datetime(
        string="Create at", default=fields.Datetime.now, readonly=True
    )

    @api.model
    def create(self, vals):
        new_record = super(Mentor, self).create(vals)
        new_record._update_user_role(new_record.email)
        return new_record

    def _update_user_role(self, email):
        User = self.env["res.users"]
        user = User.search([("login", "=", email)], limit=1)
        mentor_group = self.env.ref(
            "mentor_management.group_mentor_management_mentor"
        )

        if user:
            user.groups_id |= mentor_group
        else:
            new_user = User.create(
                {
                    "name": self.full_name,
                    "login": email,
                    "groups_id": [(4, mentor_group.id)],
                }
            )
            print(new_user)
