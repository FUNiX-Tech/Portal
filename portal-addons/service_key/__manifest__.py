# -*- coding: utf-8 -*-
{
    "name": "Service Key",
    "summary": """
    Module control service keys
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
    "depends": ["base"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/service_key_form.xml",
    ],
    # only loaded in demonstration mode
}
