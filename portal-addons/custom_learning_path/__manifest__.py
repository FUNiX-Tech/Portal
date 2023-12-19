# -*- coding: utf-8 -*-
{
    "name": "custom_learning_path",
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
        "portal_student_management",
        "course_management",
        "student_organization",
        "po_learning_program",
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/organization_learning_path_views.xml",
        "views/individual_learning_path_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
