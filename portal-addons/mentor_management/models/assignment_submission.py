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
    _inherit = 'assignment_submission'
    # _description = 'assignment_submission'

    mentor_id = fields.Many2one('mentor_management', string="Mentor",group="mentor_management.group_mentor_management_admin")
