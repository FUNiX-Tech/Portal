# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class StudentCourseAssignment(models.Model):
    _name = "business_student_course_assignment"

    name = fields.Char(string="Name")

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    business_student_id = fields.Many2one(
        comodel_name="portal.student",
        string="Business Student",
        required=True,
        domain="[('student_organization_student_ids', '=', organization_id)]",
    )

    course_id = fields.Many2one(
        comodel_name="course_management",
        string="Course",
        required=True,
        domain="[('organization_ids.student_organization_id', '=', organization_id)]",
    )

    assigned_by = fields.Many2one(
        comodel_name="portal.student",
        string="Assigned By",
        required=True,
        domain="['&',('student_organization_student_ids', '=', organization_id), ('student_role_id.name', '=', 'ADMIN')]",
    )

    assigned_date = fields.Date(
        string="Assigned Date", required=True, default=fields.Date.today()
    )

    assigned_description = fields.Html(string="Assigned Description")

    @api.model
    def create(self, vals):
        try:
            # Call the super to create the assignment record
            new_assignment = super(StudentCourseAssignment, self).create(vals)

            # Check if there is an existing student_course_data record
            student_course_data = self.env["student_course_data"].search(
                [
                    ("student_id", "=", vals.get("business_student_id")),
                    ("course_id", "=", vals.get("course_id")),
                ]
            )

            if student_course_data:
                # If exists, update the enrollment_status to True
                student_course_data.write({"enrollment_status": True})
            else:
                # If not exists, create a new record with enrollment_status True
                self.env["student_course_data"].create(
                    {
                        "student_id": vals.get("business_student_id"),
                        "course_id": vals.get("course_id"),
                        "enrollment_status": True,
                        # You can set other default values here
                    }
                )

            return new_assignment
        except Exception as e:
            raise UserError(
                "An error occurred while creating the assignment: {}".format(e)
            )


class StudentCourseGroupAssignment(models.Model):
    _name = "business_student_course_group_assignment"

    name = fields.Char(string="Name")

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    business_student_id = fields.Many2one(
        comodel_name="portal.student",
        string="Business Student",
        required=True,
        domain="[('student_organization_student_ids', '=', organization_id)]",
    )

    course_group_id = fields.Many2one(
        comodel_name="organization_course_group",
        string="Course Group",
        required=True,
        domain="[('organization_id', '=', organization_id)]",
    )

    assigned_by = fields.Many2one(
        comodel_name="portal.student",
        string="Assigned By",
        required=True,
        domain="['&', ('student_organization_student_ids', '=', organization_id), ('student_role_id.name', '=', 'ADMIN')]",
    )

    assigned_date = fields.Date(
        string="Assigned Date", required=True, default=fields.Date.today()
    )

    assigned_description = fields.Html(string="Assigned Description")

    @api.model
    def create(self, vals):
        try:
            # Call the super to create the assignment record
            new_assignment = super(StudentCourseGroupAssignment, self).create(
                vals
            )

            # Get the course group
            course_group = new_assignment.course_group_id

            # Loop through each course in the course group
            for course in course_group.course_ids:
                # Check if there is an existing student_course_data record
                student_course_data = self.env["student_course_data"].search(
                    [
                        (
                            "student_id",
                            "=",
                            new_assignment.business_student_id.id,
                        ),
                        ("course_id", "=", course.id),
                    ]
                )

                if student_course_data:
                    # If exists, update the enrollment_status
                    student_course_data.write({"enrollment_status": True})
                else:
                    # If not exists, create a new record
                    self.env["student_course_data"].create(
                        {
                            "student_id": new_assignment.business_student_id.id,
                            "course_id": course.id,
                            "enrollment_status": True,
                            # You can set other default values here
                        }
                    )

            return new_assignment

        except Exception as e:
            _logger.error(
                "Error in creating StudentCourseGroupAssignment: %s", str(e)
            )
            raise UserError(
                "An error occurred while creating the assignment: {}".format(e)
            )
