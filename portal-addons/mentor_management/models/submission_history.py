from odoo import models, fields
import datetime


class SubmissionHistory(models.Model):
    _name = "submission_history"
    _description = "Submission History"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    project_id = fields.Many2one(comodel_name="project", string="Project")
    submission_id = fields.Many2one(
        "project_submission", string="Submission ID"
    )
    created_at = fields.Datetime(
        string="Submission Time", default=fields.Datetime.now, required=True
    )
    status = fields.Selection(
        [
            ("not_submitted", "Not submitted"),
            ("submission_failed", "Submission failed"),
            ("submitted", "Submitted"),
            ("submission_cancelled", "Submission cancelled"),
            ("grading", "Grading"),
            ("graded", "Graded"),
        ],
        string="Status",
        default="not_submitted",
        required=True,
    )

    def _get_submissions_for_reminder(self):
        # get interval sla time reminder from config key module
        sla_reminder_interval = int(
            self.env["service_key_configuration"].get_api_key_by_service_name(
                "SLA_MENTOR_REMINDER_TIME_IN_DAY"
            )
        )

        # Lấy tất cả các bản ghi
        all_histories = self.search([])

        # Lọc ra danh sách các submission_id duy nhất
        unique_submission_ids = set(
            [history.submission_id.id for history in all_histories]
        )
        print("all_histories", all_histories)
        print("unique_submission_ids", unique_submission_ids)

        # Lọc ra những submissions cần nhắc nhở
        submissions_for_reminder = []
        for submission_id in unique_submission_ids:
            # Lấy ra submission_history mới nhất cho mỗi submission_id
            latest_history = self.search(
                [("submission_id", "=", submission_id)],
                order="created_at desc",
                limit=1,
            )
            print("latest_history.created_at", latest_history.created_at)
            diff_day = (fields.Datetime.now() - latest_history.created_at).days
            print(diff_day)
            if (
                latest_history
                and latest_history.status == "grading"
                and diff_day != 0
                and diff_day % sla_reminder_interval == 0
            ):
                submissions_for_reminder.append(latest_history)

        print("submissions_for_reminder", submissions_for_reminder)

        return submissions_for_reminder

    def send_reminder_emails(self):
        list_submissions_for_reminder = self._get_submissions_for_reminder()
        for submission in list_submissions_for_reminder:
            title = "Reminder: Project Submission Grading"
            # subject
            subject = "Please Grade the Project Submission"
            # tạo nội dung mail
            body = f"""<div>
            <h2>Hello {submission.submission_id.mentor_id.full_name},</h2>
            <h3>You have an Project Submission to evaluate</h3>
            <p>Assignment: {submission.assignment_id.title}</p>
            <p>Course name: {submission.assignment_id.course.course_name}</p>
            <p>Couse code: {submission.assignment_id.course.course_code}</p>
            <p>I hope you happy with that</p>
            <strong>Thank you!</strong>
            <div>"""
            # description
            description = "Grading Reminder"
            # external_link
            external_link = submission.submission_id.submission_url
            # external_text
            external_text = "Go to Project Submission"
            # gửi mail
            submission.submission_id.send_email(
                instance_model=submission.submission_id,
                to_email=submission.submission_id.mentor_id.email,
                title=title,
                subject=subject,
                body=body,
                description=description,
                external_link=external_link,
                external_text=external_text,
            )
