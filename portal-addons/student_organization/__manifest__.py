# -*- coding: utf-8 -*-
{
    "name": "Student Organization",
    "summary": """
     Student Organization module for CRUD Student
    """,
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
    "depends": ["base", "portal_student_management"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/student_organization_views.xml",
        "views/student_student_organization.xml",
    ],
    # only loaded in demonstration mode
}
