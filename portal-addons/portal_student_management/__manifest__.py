# -*- coding: utf-8 -*-
{
    "name": "Portal Student Management",
    "version": "1.0",
    # Tóm tắt module
    "summary": """
        Module used to manage students, students can register, login via API, admin can add, edit, delete students.
    """,
    # Mô tả các chức năng trong module
    "description": """
        1. Admin can add, edit, delete students.
        2. Teacher can view list of students.
        3. API Student Register.
        4. API Login.
        5. API Update Student Information.
    """,
    # Tác giả
    "author": "khoansfx",
    # Phân loại module
    "category": "portal_addons",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/student_actions.xml",
        "views/student_view_menu.xml",
        "views/student_view_form.xml",
        "views/student_view_tree.xml",
    ],
    # Các dependencies :
    # 1. base : module cơ bản của odoo
    "depends": ["base", "service_key", "mail_service"],
    "external_dependencies": {
        "python": ["secrets", "pyjwt", "uuid"],
    },
    "assets": {
        "web.assets_backend": [
            "portal_student_management/static/src/css/custom_styles.css",
        ],
    },
    # Khác:
    "auto_install": False,
    "installable": True,
}
