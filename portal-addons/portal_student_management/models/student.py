
# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
import random
import re
from werkzeug.security import generate_password_hash


class Student(models.Model):
    _name = "portal.student"
    _description = "Student Information"

    name = fields.Char(string='Student Name', required=True)
    email = fields.Char(string='Email', required=True, unique=True, index=True)
    student_code = fields.Char(string='Student Code', readonly=True)
    date_of_birth = fields.Date(string='Date of birth')
    password_hash = fields.Char(string='Password')
    phone = fields.Char(string='Phone')
    gender = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'khác')],
        required=True,
        default='male'
    )
    email_verified_status = fields.Boolean(
        string='Veriied Email', default=False)
    created_at = fields.Datetime(
        string='Created At', readonly=True, default=fields.Datetime.now())
    updated_at = fields.Datetime(
        string='Updated At', readonly=True, default=fields.Datetime.now())

    @api.model
    def _student_code_generator(self, student_dict):
        """
        Function is called when creating a new student. Check to see if the student has a student_code yet. If not, create a new one, when creating a new one if it is duplicated, it will create a new student_code until it is not duplicated.

        @params:
            dict: student_dict: Student data sent from the form
            self: Student object

        @return: int: student_code: Student code

        """
        student_code = student_dict.get('student_code')

        if not student_code:
            while True:
                # !TODO: Student code generator, need to change the algorithm to suit the needs
                # zfill(6) to fill 0 to reach 6 numbers => 000001, 000002, 000003,... -> string
                new_student_code = str(random.randint(1, 100000)).zfill(6)

                # Check if the student_code is already in the database
                if not self.env['portal.student'].search([('student_code', '=', new_student_code)]):
                    student_code = new_student_code
                    break

        return student_code

    # ==================== VALIDATION ====================

    @api.constrains('phone')
    def _check_phone(self):
        """
        Check if the phone number is valid. Use regex to check if the phone number is in the correct format

        @params:
        1. self: Student object

        @return: validation error if phone number is invalid

        @decorator: api.constrains to call the function when creating or updating a Student object
        """

        # Check if the phone number is valid
        # !TODO: Replace the regex with the correct phone number format for stronger validation
        pattern = r'^\d+$'
        for record in self:
            if record.phone and not re.match(pattern, record.phone):
                raise exceptions.ValidationError('Invalid phone number')

    @api.constrains('email')
    def _check_email(self):
        """
        Check if the email is valid. Use regex to check if the email is in the correct format

        @params: 
        1. self: Student Object

        @return: validation error if email is invalid 

        @decorator: api.constrains to call the function when creating or updating a Student object
        """
        for record in self:
            # Check if the email is valid
            # Link Regex: https://regex101.com/r/O9oCj8/1
            if record.email and not re.match(r"^[^\.\s][\w\-\.{2,}]+@([\w-]+\.)+[\w-]{2,}$", record.email):
                raise exceptions.ValidationError('Invalid email')

    # ==================== OVERRIDE MODEL METHOD ====================

    def write(self, student_dict):
        """
        Update the student information. Update the 'updated_at' field with the current datetime
        """
        # Update the 'updated_at' field with the current datetime
        student_dict['updated_at'] = fields.Datetime.now()

        if 'password_hash' in student_dict and len(student_dict['password_hash']) < 32:
            student_dict['password_hash'] = generate_password_hash(
                student_dict['password_hash'])

        # Check if the email already exists in the database
        if 'email' in student_dict:
            if student_dict['email'] and self.env['portal.student'].search([('email', '=', student_dict['email'])]):
                raise exceptions.ValidationError('Email already exists')

        return super(Student, self).write(student_dict)

    @api.model
    def create(self, student_dict):
        """
        Function is called when creating a new student. Check to see if the student has a student_code yet. If not, create a new one, when creating a new one if it is duplicated, it will create a new student_code until it is not duplicated.

        @params:
            dict: student_dict: Student data sent from the form
            self: Student Object

        """
        student_dict['student_code'] = self._student_code_generator(
            student_dict)
        # Kiểm tra email đã tồn tại trong database chưa
        if student_dict['email'] and self.env['portal.student'].search([('email', '=', student_dict['email'])]):
            raise exceptions.ValidationError('Email already exists')
        self._check_phone()

        return super(Student, self).create(student_dict)
