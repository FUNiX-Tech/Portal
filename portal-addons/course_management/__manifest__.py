# -*- coding: utf-8 -*-
{
    "name": "Course Management",
    "summary": """
        Course Management Module for CRUD course""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Funix",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "portal_student_management", "student_organization"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/course_management_views.xml",
        # "views/course_for_organization_view.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
