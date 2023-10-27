
# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
import random
import re


class Student(models.Model):
    _name = "portal.student"
    _description = "Thông tin học viên"

    name = fields.Char(string='Họ tên', required=True)
    email = fields.Char(string='Email', required=True, unique=True, index=True)
    student_code = fields.Char(string='Mã học viên', readonly=True)
    date_of_birth = fields.Date(string='Ngày sinh')
    password_hash = fields.Char(string='Mật khẩu')
    phone = fields.Char(string='Số điện thoại')
    gender = fields.Selection(
        string='Giới tính',
        selection=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'khác')],
        required=True,
        default='male'
    )
    email_verified_status = fields.Boolean(
        string='Xác thực email', default=False)
    created_at = fields.Datetime(
        string='Ngày tạo', readonly=True, default=fields.Datetime.now())
    updated_at = fields.Datetime(
        string='Ngày cập nhật', readonly=True, default=fields.Datetime.now())

    @api.model
    def _student_code_generator(self, student_dict):
        """
        Hàm này được gọi khi tạo mới học viên. Kiếm tra xem học viên đã có student_code chưa. Nếu chưa có thì tạo mới, khi tạo mới nếu trùng thì sẽ tạo lại student_code mới đến khi nào không trùng thì thôi.

        @params:
            dict: student_dict: Dữ liệu học viên được gửi từ form
            self: Đối tượng Student

        @return: int: student_code: Mã học viên mới được tạo ra

        @Decorator: api.model để gọi hàm mà không cần tạo đối tượng (như hàm self.create(), self.search(),...)



        """
        student_code = student_dict.get('student_code')

        if not student_code:
            while True:
                # !TODO: Tạo mã học viên ngẫu nhiên - Thay đổi logic để phù hợp với yêu cầu
                # zfill(6) để thêm số 0 vào đầu cho đủ 6 chữ số => 000001, 000002, 000003,... -> string
                new_student_code = str(random.randint(1, 100000)).zfill(6)

                # Kiểm tra mã học viên có trùng với ai trong database không
                if not self.env['portal.student'].search([('student_code', '=', new_student_code)]):
                    student_code = new_student_code
                    break

        return student_code

    # ==================== VALIDATION ====================

    @api.constrains('phone')
    def _check_phone(self):
        """
        Hàm để kiểm tra số điện thoại có hợp lệ không. Sử dụng regex để kiểm tra số điện thoại có đúng định dạng không

        @params:
        1. self: Đối tượng Student

        @return: validation error nếu số điện thoại không hợp lệ

        @decorator: api.constrains để gọi hàm khi tạo mới hoặc cập nhật đối tượng Student
        """

        # Kiểm tra số điện thoại có hợp lệ không, chỉ chấp nhận số
        # !TODO: Thay đổi pattern phù hợp với nhu cầu
        pattern = r'^\d+$'
        for record in self:
            if record.phone and not re.match(pattern, record.phone):
                raise exceptions.ValidationError('Số điện thoại không hợp lệ')

    @api.constrains('email')
    def _check_email(self):
        """
        Hàm để kiểm tra email có hợp lệ không. Sử dụng regex để kiểm tra email có đúng định dạng không

        @params: 
        1. self: Đối tượng Student

        @return: validation error nếu email không hợp lệ 

        @decorator: api.constrains để gọi hàm khi tạo mới hoặc cập nhật đối tượng Student
        """
        for record in self:
            # Kiểm tra email có hợp lệ không
            # Link Regex: https://regex101.com/r/O9oCj8/1
            if record.email and not re.match(r"^[^\.\s][\w\-\.{2,}]+@([\w-]+\.)+[\w-]{2,}$", record.email):
                raise exceptions.ValidationError('Email không hợp lệ')

    # ==================== OVERRIDE MODEL METHOD ====================

    def write(self, student_dict):
        """
        Hàm để cập nhật field updated_at khi cập nhật thông tin học viên
        """
        # Update the 'updated_at' field with the current datetime
        student_dict['updated_at'] = fields.Datetime.now()
        return super(Student, self).write(student_dict)

    @api.model
    def create(self, student_dict):
        """
        Hàm này được gọi khi tạo mới học viên. Kiếm tra xem học viên đã có student_code chưa. Nếu chưa có thì tạo mới, khi tạo mới nếu trùng thì sẽ tạo lại student_code mới đến khi nào không trùng thì thôi.

        @params:
            dict: student_dict: Dữ liệu học viên được gửi từ form
            self: Đối tượng Student

        @Decorator: api.model để gọi hàm mà không cần tạo đối tượng (như hàm self.create(), self.search(),...)



        """
        student_dict['student_code'] = self._student_code_generator(
            student_dict)
        self._check_phone()

        return super(Student, self).create(student_dict)
