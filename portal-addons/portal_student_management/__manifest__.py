# -*- coding: utf-8 -*-
{
    'name': "portal_student_management",

    # Tóm tắt module
    'summary': """
        Module dùng để quản lý học viên, học viên có thể đăng ký, đăng nhập, admin có thể thêm mới, sửa, xóa học viên.
    """,

    # Mô tả các chức năng trong module
    'description': """
        1. Admin có thể thêm mới, sửa, xóa học viên. 
        2. Học viên có thể xem thông tin cá nhân, thay đổi mật khẩu và sửa thông tin cá nhân.
        3. API đăng ký học viên mới.
        4. API đăng nhập
        5. API để cập nhật thông tin cá nhân của học viên.
    """,

    # Tác giả
    'author': "khoansfx",

    # Phân loại module
    'category': 'portal_addons',
    'version': '0.1',

    
    'data':[],

    # Các dependencies : 
    # 1. base : module cơ bản của odoo
    'depends': ['base'],
}
