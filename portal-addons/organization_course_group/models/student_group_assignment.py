# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class StudentGroupCourseAssignment(models.Model):
    _name = "student_group_course_assignment"

    name = fields.Char(string="Name", required=True)

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    student_group_id = fields.Many2one(
        comodel_name="student_group",
        string="Student Group",
        required=True,
        domain="[('group_organization_id', '=', organization_id)]",
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
            new_assignment = super(StudentGroupCourseAssignment, self).create(
                vals
            )

            # Get the assigned student group
            student_group = new_assignment.student_group_id

            # Iterate over each student in the group
            for student in student_group.business_student_ids:
                # Check if there is an existing student_course_data record
                student_course_data = self.env["student_course_data"].search(
                    [
                        ("student_id", "=", student.id),
                        ("course_id", "=", new_assignment.course_id.id),
                    ]
                )

                if student_course_data:
                    # If exists, update the enrollment_status
                    student_course_data.write({"enrollment_status": True})
                else:
                    # If not exists, create a new record
                    self.env["student_course_data"].create(
                        {
                            "student_id": student.id,
                            "course_id": new_assignment.course_id.id,
                            "enrollment_status": True,
                            # You can set other default values here
                        }
                    )

            return new_assignment
        except Exception as e:
            raise UserError(
                "An error occurred while creating the group course assignment: {}".format(
                    e
                )
            )


class StudentGroupCourseGroupAssignment(models.Model):
    _name = "student_group_course_group_assignment"

    name = fields.Char(string="Name", required=True)

    organization_id = fields.Many2one(
        comodel_name="student_organization",
        string="Organization",
        required=True,
    )

    student_group_id = fields.Many2one(
        comodel_name="student_group",
        string="Student Group",
        required=True,
        domain="[('group_organization_id', '=', organization_id)]",
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
            # Call the super to create the group course group assignment record
            new_assignment = super(
                StudentGroupCourseGroupAssignment, self
            ).create(vals)

            # Get the assigned student group
            student_group = new_assignment.student_group_id
            # Get the assigned course group
            course_group = new_assignment.course_group_id

            # Iterate over each student in the group
            for student in student_group.business_student_ids:
                # Iterate over each course in the course group
                for course in course_group.course_ids:
                    # Check if there is an existing student_course_data record
                    student_course_data = self.env[
                        "student_course_data"
                    ].search(
                        [
                            ("student_id", "=", student.id),
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
                                "student_id": student.id,
                                "course_id": course.id,
                                "enrollment_status": True,
                                # You can set other default values here
                            }
                        )

            return new_assignment
        except Exception as e:
            raise UserError(
                "An error occurred while creating the group course group assignment: {}".format(
                    e
                )
            )
