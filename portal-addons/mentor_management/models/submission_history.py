from odoo import models, fields
import datetime


class SubmissionHistory(models.Model):
    _name = "submission_history"
    _description = "Submission History"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True
    )
    assignment_id = fields.Many2one("assignment", string="Assignment")
    submission_id = fields.Many2one(
        "assignment_submission", string="Submission ID"
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
        # time_to_remind = fields.Datetime.now() - datetime.timedelta(days=2)
        time_to_remind = fields.Datetime.now() - datetime.timedelta(minutes=1)
        submission_histories = self.search(
            [("status", "=", "grading"), ("created_at", "<=", time_to_remind)]
        )
        return submission_histories

    def send_reminder_emails(self):
        submissions = self._get_submissions_for_reminder()
        for submission in submissions:
            # send mail to mentor, remind mentor to grade the assignment
            # mentor email
            # if "mentor_id" in submission:
            #     to_email = submission.mentor_id.email
            # title
            title = "Reminder: Assignment Submission Grading"
            # subject
            subject = "Please Grade the Assignment Submission"
            # tạo nội dung mail
            body = f"""<div>
            <h2>Hello mentor</h2>
            <h3>You have an Learning Project Submission to grade</h3>
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
            external_text = "View Submission"
            # gửi mail
            submission.submission_id.send_email(
                instance_model=submission.submission_id,
                to_email="hajime3419@gmail.com",
                title=title,
                subject=subject,
                body=body,
                description=description,
                external_link=external_link,
                external_text=external_text,
            )

            # tại sao ở đoạn code trên lúc truyền vào instance_model=submission.id
            # mà không phải là instance_model=submission
            # vì khi gọi hàm send_email trong models.py
            # hàm send_email đã được gọi trong một vòng lặp
            # nên instance_model phải là một id
            # nếu không sẽ bị lỗi
            # TypeError: 'submission_history' model does not exist
