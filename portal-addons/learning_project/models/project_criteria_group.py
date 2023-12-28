# -*- coding: utf-8 -*-

from odoo import models, fields, api

UNIQUE_TITLE_PROJECT = (
    "unique_criteria_group_title",
    "unique(title, project)",
    "The titles of criteria Groups must be unique within a project.",
)
UNIQUE_NUMBER_PROJECT = (
    "unique_criteria_group_number",
    "unique(number, project)",
    "The numbers of criteria Groups must be unique within a project.",
)


class ProjectCriteriaGroup(models.Model):
    _name = "project_criteria_group"
    _description = "project_criteria_group"
    _rec_name = "title"

    title = fields.Char(string="Criteria Group Name", required=True)

    criteria = fields.One2many(
        "project_criterion",
        inverse_name="criteria_group",
        string="Criteria",
    )

    number = fields.Integer(string="Number", required=True, default=1)

    project = fields.Many2one("project", required=True, ondelete="cascade")

    _sql_constraints = [
        UNIQUE_TITLE_PROJECT,
        UNIQUE_NUMBER_PROJECT,
    ]

    @api.model
    def create(self, vals):
        largest_group = self.env["project_criteria_group"].search(
            [("project", "=", self.env.context.get("default_project"))],
            order="number DESC",
            limit=1,
        )

        if largest_group:
            vals["number"] = largest_group.number + 1
        else:
            vals["number"] = 1

        vals["project"] = self.env.context.get("default_project")

        return super(ProjectCriteriaGroup, self).create(vals)
