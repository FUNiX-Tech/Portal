# -*- coding: utf-8 -*-
{
    "name": "Funix Learning ProjectGrading Template",
    "summary": "Learning Project Feedback Template",
    "description": "Learning Project Feedback Template",
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/grading_template_category_views.xml",
        "views/grading_template_views.xml",
    ],
}
