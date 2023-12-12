from odoo import models, fields, api


class CourseManagement(models.Model):
    _inherit = "course_management"

    student_ids = fields.Many2many(
        "portal.student",
        "student_course_rel",
        "course_id",
        "student_id",
        string="Students Enrolled",
    )
    # progress = fields.Char(
    #     string="Course Progress", computed="_compute_progress", store=False
    # )
    min_watches = fields.Float(string="Mins. watched", default=125)
    last_activity = fields.Datetime(
        default=fields.Datetime.now, string="Last Activity"
    )
    display_time = fields.Char(
        string="Mins. watched", compute="_compute_display_time", store=True
    )
    assignment = fields.Char(string="Assignment")
    days_ago = fields.Char(
        string="Last Activity", compute="_compute_days_ago", store=True
    )

    @api.depends("min_watches")
    def _compute_display_time(self):
        for record in self:
            hours = int(record.min_watches / 60)
            minutes = int(record.min_watches % 60)
            if hours > 0 and minutes > 0:
                record.display_time = f"{hours} hours {minutes} minutes"
            elif hours > 0:
                record.display_time = f"{hours} hours"
            elif minutes > 0:
                record.display_time = f"{minutes} minutes"
            else:
                record.display_time = "0 minutes"

    @api.depends("last_activity")
    def _compute_days_ago(self):
        for record in self:
            if record.last_activity:
                time_difference = fields.Datetime.now() - record.last_activity
                days_ago = int(time_difference.days)
                if days_ago == 0:
                    record.days_ago = "Today"
                elif days_ago == 1:
                    record.days_ago = "Yesterday"
                else:
                    record.days_ago = f"{days_ago} days ago"
            else:
                record.days_ago = "N/A"
