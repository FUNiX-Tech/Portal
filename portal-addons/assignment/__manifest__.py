# -*- coding: utf-8 -*-
{
    'name': "assignment",

    'summary': """
    Assignment
    """,

    'description': """
        Assignment
    """,

    'author': "portal",
    'website': "https://www.portal.example.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/assignment_views.xml',
        'views/assignment_criterion_group_views.xml',
        'views/assignment_criterion_views.xml',
    ],
}
