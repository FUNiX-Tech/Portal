# -*- coding: utf-8 -*-
{
    "name": "Custom List View",
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
    "data": [
        "report/custom_list_view_templates.xml",
        "report/custom_list_view_reports.xml",
    ],
    # any module necessary for this one to work correctly
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "custom_list_view/static/src/**/*",
        ]
    },
}
