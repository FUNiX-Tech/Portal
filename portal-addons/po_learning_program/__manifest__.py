# -*- coding: utf-8 -*-
{
    "name": "PO Learning Program",
    "summary": """
     Adding students into Learning Program
     Adding courses into Learning Program
     """,
    "description": """
        Long description of module's purpose
    """,
    "author": "funix",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "course_management"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/student_course_data.xml",
        "views/po_learning_program_views.xml",
        "views/learning_program_access.xml",
        "views/course_access.xml",
        "views/course_management_views.xml",
        "views/organization_views.xml",
        "views/student_views.xml",
    ],
}
