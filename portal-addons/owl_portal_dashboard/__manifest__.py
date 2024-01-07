# -*- coding: utf-8 -*-
{
    'name': "Portal Dashboard",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',"web",'portal_student_management','course_management'],

    # always loaded
    'data': [
        "views/portal_student_inherit/student_list_inherit.xml",
        "views/course_management_inherit/course_list_inherit.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'owl_portal_dashboard/static/src/components/*/*/*.js',
            'owl_portal_dashboard/static/src/components/*/*/*.xml',
            'owl_portal_dashboard/static/src/components/*/*/*.scss',
            'owl_portal_dashboard/static/src/scss/*.scss',
        ],
    },
}
