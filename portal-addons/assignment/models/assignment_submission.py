# -*- coding: utf-8 -*-
"""
Need to set the following variables to config file: 
- lms_submission_notification: the lms url to send submission result notification.
- email_from: sender email (e.g. notification@example.com)
"""


import logging
import requests
from odoo import models, fields, api
from odoo.tools import config

logger = logging.getLogger(__name__)

class AssignmentSubmission(models.Model):
    _name = 'assignment_submission'
    _description = 'assignment_submission'

    MAIL_SENDER = config.get("email_from")

    NOT_GRADED = ("not_graded", "Not Graded")
    PASSED = ("passed", "Passed")
    DID_NOT_PASS = ("did_not_pass", "Did Not Pass")
    UNABLE_TO_REVIEW = ("unable_to_review", "Unable to Review")
    DEFAULT_RESULT = NOT_GRADED[0]

    student = fields.Many2one('portal.student', string="Học viên", readonly=True) 
    assignment = fields.Many2one("assignment", string="Assignment", readonly=True) 
    submission_url = fields.Char(string="Submission Url", readonly=True) 
    criteria_responses = fields.One2many("assignment_criterion_response", inverse_name="submission", string="Các tiêu chí") 
    result = fields.Selection([ NOT_GRADED, PASSED, DID_NOT_PASS, UNABLE_TO_REVIEW ], required=True, string="Kết quả", default=DEFAULT_RESULT, readonly=True)

    has_graded_all_criteria = fields.Boolean(compute="_has_graded_all_criteria", store=True)
    course = fields.Char(related='assignment.course.course_name')

    @api.depends("criteria_responses.result")
    def _has_graded_all_criteria(self):
        for record in self:

            graded_all = True
            for repsonse in record.criteria_responses:
                if repsonse.result == self.NOT_GRADED[0]:
                    graded_all = False
                    break
            
            record.has_graded_all_criteria = graded_all
            
    def submit_grade(self):
        """
        After graded all the criteria, mentor should click the submit button to trigger this function. 
        TODO:
            - Calculate and set the final result to the submission according to its criteria.
            - Send notification email to the student. 
            - Send notification request to lms. 
        """
        for record in self:
            if record.has_graded_all_criteria:
                if any(response.result == self.UNABLE_TO_REVIEW[0] for response in record.criteria_responses):
                    record.result = self.UNABLE_TO_REVIEW[0]
                elif any(response.result == self.DID_NOT_PASS[0] for response in record.criteria_responses):
                    record.result = self.DID_NOT_PASS[0]
                else:
                    record.result = self.PASSED[0]

                self._send_notification_email_to_student()
                self._send_notification_request_to_lms()
                    
                return True
            return False

    def _send_notification_email_to_student(self):
        """
        NEED TO READ MORE AND HANDLE EXCEPTION!!!
        mail_template.send_mail(self.id, force_send=True) doesn't raise an exception if it fails to send an email.
        """
        for record in self: 
            try: 
                mail_template = self.env.ref('assignment.submission_result_notification_email_template')
                mail_template.send_mail(self.id, force_send=True)
                logger.info(f"[Assignment Submission]: Sent notification email to '{record.student.email}'")
                return True
            except Exception as e:
                logger.error(str(e))
                logger.error(f"[Assignment Submission]: Failed to send notification email to '{record.student.email}'")
                return False

    def _send_notification_request_to_lms(self):      
        for record in self: 
            headers = {'Content-Type': 'application/json'}
            payload = {
                    'data': {
                        'submission_id': record.id,
                        'student_id': record.student.id,
                        'result': record.result
                    }, 
                    'message': 'Submission has been graded'
                }
            
            try: 
                url = config.get('lms_submission_notification')
                response = requests.post(url, headers=headers, json=payload)
            
                if response.status_code == 200:
                    logger.info("[Assignment Submission]: Sent notification email to LMS")
                    return True
                else:
                    logger.error(f"[Assignment Submission]: Failed to send notification email to LMS", response.text)
                    return False
            except Exception as e: 
                logger.error(f"[Assignment Submission]: Failed to send notification email to LMS", str(e))
                return False