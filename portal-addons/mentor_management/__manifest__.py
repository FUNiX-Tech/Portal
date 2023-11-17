# -*- coding: utf-8 -*-
{
    "name": "mentor_management",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Allen Walker",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "assignment",
        "course_management",
        "mail",
        "mail_service",
        "service_key",
    ],
    # always loaded
    "data": [
        "security/mentor_security.xml",
        "security/ir.model.access.csv",
        "views/mentor_view.xml",
        "views/assignment_submission_views.xml",
        "views/assignment_views.xml",
        "data/mentor_management_extension_sequence.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
