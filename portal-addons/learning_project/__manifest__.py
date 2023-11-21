# -*- coding: utf-8 -*-
{
    "name": "Project",
    "summary": "Learning Project",
    "description": "Learning Project",
    "author": "portal",
    "website": "https://www.portal.example.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "email_server_config",
        "portal_student_management",
        "course_management",
        "mail",
        "mail_service",
        "service_key",
    ],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/project_criterion_response_views.xml",
        "views/project_criterion_views.xml",
        "views/project_submission_views.xml",
        "views/project_views.xml",
        "views/graded_email_template.xml",
    ],
}
