# -*- coding: utf-8 -*-
{
    "name": "Feedback Ticket Management",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "mail",
        "portal_student_management",
        "course_management",
        "service_key",
    ],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/tickets_view.xml",
        "data/ticket_sequence.xml",
        "data/assign_email_template.xml",
        "data/email_server.xml",
        "data/response_email_template.xml",
        "data/email_assignee_reminder_template.xml",
        "data/schedule_remind_assignee.xml",
        "views/setting_config_key.xml",
    ],
}
