from odoo import fields, models, api


class StudentCourse(models.Model):
    _name = "student.course"
    _description = "Student Course Relationship"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    course_id = fields.Many2one(
        "course_management", string="Course", required=True
    )
    _sql_constraints = [
        (
            "unique_student_course",
            "unique(student_id, course_id)",
            "Student and Course must be unique.",
        ),
    ]

    course_progress = fields.Char(
        string="Course Progress", default="0 lessons"
    )
    last_activity = fields.Char(string="Last Activity", default="1 days ago")

    @api.model
    def migrate_student_course_relation(self):
        migrate_check = self.env[
            "service_key_configuration"
        ].get_api_key_by_service_name("MIGRATE_CHECK")
        if migrate_check and migrate_check == "True":
            list_student = self.env["portal.student"].sudo().search([])
            for student in list_student:
                # Example: Assuming course_id is a fixed value, adjust accordingly
                list_course = student.course_ids
                for course in list_course:
                    # Check if the record already exists
                    existing_record = self.search(
                        [
                            ("student_id", "=", student.id),
                            ("course_id", "=", course.id),
                        ]
                    )
                    # If the record doesn't exist, create it
                    if not existing_record:
                        self.create(
                            {
                                "student_id": student.id,
                                "course_id": course.id,
                            }
                        )
        else:
            return
