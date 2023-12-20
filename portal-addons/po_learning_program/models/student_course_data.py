from odoo import fields, models, api

import requests


class StudentCourse(models.Model):
    _name = "student_course_data"
    _description = "Student Course Relationship"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    course_id = fields.Many2one(
        "course_management", string="Course", required=True
    )

    enrollment_status = fields.Boolean(
        string="Enrollment Status", default=True
    )

    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.today(),
    )

    learning_progress = fields.Char(string="Learning Progress", default="N/A")

    organization_name = fields.Char(
        string="Organization Name", compute="_compute_organization_name"
    )

    @api.depends("student_id")
    def _compute_organization_name(self):
        for record in self:
            if (
                record.student_id
                and record.student_id.student_organization_student_ids
            ):
                record.organization_name = (
                    record.student_id.student_organization_student_ids.name
                )
            else:
                record.organization_name = "None"

    def _fetch_and_update_learning_progress(self):
        for record in self:
            # Replace with actual API endpoint and parameters
            api_url = "..."
            params = {
                "student_id": record.student_id.external_identifier,  # Assuming external_identifier is the ID in the external system
                "course_id": record.course_id.external_identifier,  # Same assumption as above
            }
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                progress_data = response.json()
                # Assuming the response contains progress in a specific format
                completed_lessons = progress_data["completed_lessons"]
                total_lessons = progress_data["total_lessons"]
                record.learning_progress = (
                    f"{completed_lessons}/{total_lessons} lessons done"
                )
            else:
                # Handle errors (e.g., log them or set a default value)
                record.learning_progress = "Error fetching progress"

    def scheduled_update_learning_progress(self):
        # Method to be called by the Cron Job
        self.fetch_and_update_learning_progress()


class Student(models.Model):
    _inherit = "portal.student"

    course_ids = fields.One2many(
        "student_course_data", inverse_name="student_id", string="Courses"
    )


class Course(models.Model):
    _inherit = "course_management"

    student_ids = fields.One2many(
        "student_course_data", inverse_name="course_id", string="Students"
    )
