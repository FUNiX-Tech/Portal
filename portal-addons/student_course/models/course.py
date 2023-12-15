from odoo import models, fields, api
import datetime

# dictionary to get colour for status and result
DICT_COLOR_STATUS = {
    "graded": "success",
    "submitted": "info",
    "submission_failed": "danger",
    "submission_cancelled": "danger",
    "grading": "warning",
}
DICT_COLOR_RESULT = {
    "passed": "success",
    "did_not_pass": "danger",
    "incomplete": "warning",
    "unable_to_review": "warning",
}


class CourseManagement(models.Model):
    _inherit = "course_management"

    student_ids = fields.Many2many(
        "portal.student",
        "student_course_rel",
        "course_id",
        "student_id",
        string="Students Enrolled",
    )
    course_progress = fields.Char(
        string="Progress",
        compute="_compute_active_id_display",
        readonly=True,
        store=False,
        default="0 lessons",
    )
    last_activity = fields.Char(
        string="Last Activity",
        compute="_compute_active_id_display",
        readonly=True,
        store=False,
        default="Unaccessed",
    )
    learning_project = fields.Char(
        string="Projects",
        store=False,
        compute="_compute_active_id_display",
        readonly=True,
        default="",
    )

    def _compute_active_id_display(self):
        student_id = self.env.context.get("active_id")
        for record in self:
            if student_id:
                # Get data progress and last activity  from student_course table
                student_course = (
                    self.env["student.course"]
                    .sudo()
                    .search(
                        [
                            ("student_id", "=", student_id),
                            ("course_id", "=", record.id),
                        ]
                    )
                )
                # Get all related project from course
                list_project = self.env["project"].search(
                    [("course", "=", record.id)]
                )
                project_name_status = ""
                for project in list_project:
                    list_submission = self.env["project_submission"].search(
                        [
                            ("student", "=", student_id),
                            ("project", "=", project.id),
                        ]
                    )
                    if list_submission:
                        # Get last submission to find out status
                        last_submission = list_submission[-1]
                        # if status is graded we will show the result else whe we display status as normal
                        if (
                            last_submission.latest_submission_status
                            == "graded"
                        ):
                            project_status = dict(
                                last_submission._fields["result"].selection
                            ).get(last_submission.result)
                            decoration_color = DICT_COLOR_RESULT.get(
                                last_submission.result, "muted"
                            )
                        # else will show status of submission
                        else:
                            project_status = dict(
                                last_submission._fields[
                                    "latest_submission_status"
                                ].selection
                            ).get(last_submission.latest_submission_status)
                            decoration_color = DICT_COLOR_STATUS.get(
                                last_submission.latest_submission_status,
                                "muted",
                            )
                    # if no any submission, show the project name with status not submitted
                    else:
                        project_status = "Not Submitted"
                        decoration_color = "muted"
                    project_name_status = (
                        project_name_status
                        + f"""
                            <div class='d-flex o_field_widget o_readonly_modifier o_field_badge mb-2 text-center gap-2'>
                            <p class='m-0'><strong>{project.title}:</strong></p> <span class='badge larger-badge rounded-pill text-bg-{decoration_color}'>{project_status}</span>
                            </div>
                            """
                    )
                # assign value to computed view if all condition pass
                record.learning_project = project_name_status
                if student_course:
                    record.course_progress = student_course.course_progress
                    record.last_activity = student_course.last_activity
                else:
                    record.course_progress = "0 lessons"
                    record.last_activity = "Unaccessed"
            # If no id it will set default value for all computed value
            else:
                record.course_progress = "0 lessons"
                record.last_activity = "Unaccessed"
                record.learning_project = ""
