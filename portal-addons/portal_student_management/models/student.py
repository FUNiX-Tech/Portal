# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
import random
import re
import string
import requests
import logging

_logger = logging.getLogger(__name__)


class Student(models.Model):
    _name = "portal.student"
    _description = "Student Information"
    name = fields.Char(string="Student Name", required=True)
    username = fields.Char(string="Username", required=True, unique=True)
    email = fields.Char(string="Email", required=True, unique=True, index=True)
    student_code = fields.Char(string="Student Code", readonly=True)
    date_of_birth = fields.Date(string="Date of birth")
    phone = fields.Char(string="Phone")
    gender = fields.Selection(
        string="Gender",
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("unknown", "Unknown"),
        ],
        required=True,
        default="unknown",
    )
    email_verified_status = fields.Boolean(
        string="Veriied Email", default=False
    )
    created_at = fields.Datetime(
        string="Created At", readonly=True, default=fields.Datetime.now()
    )

    @api.model
    def _student_code_generator(self, student_dict):
        """
        Function is called when creating a new student. Check to see if the student has a student_code yet. If not, create a new one, when creating a new one if it is duplicated, it will create a new student_code until it is not duplicated.

        @params:
            dict: student_dict: Student data sent from the form
            self: Student object

        @return: int: student_code: Student code

        """
        _logger.info("PSM: Generating student code")
        student_code = student_dict.get("student_code")
        _logger.debug("PSM: Student code: %s", student_code)

        if not student_code:
            _logger.info(
                "PSM: Student code is not found, generating new student code"
            )
            while True:
                # !TODO: Student code generator, need to change the algorithm to suit the needs
                # zfill(6) to fill 0 to reach 6 numbers => 000001, 000002, 000003,... -> string
                new_student_code = str(random.randint(1, 100000)).zfill(6)
                _logger.debug("PSM: New student code: %s", new_student_code)

                # Check if the student_code is already in the database
                if not self.env["portal.student"].search(
                    [("student_code", "=", new_student_code)]
                ):
                    _logger.info(
                        "PSM: Student code %s is not found in the database",
                    )
                    student_code = new_student_code
                    _logger.debug(
                        "PSM: Assigned Student code: %s", student_code
                    )
                    break

        _logger.debug("PSM: Final Student code: %s", student_code)
        return student_code

    def _generate_fixed_length_password(self, length):
        # Define the character set from which to generate the password
        characters = string.ascii_letters + string.digits + string.punctuation

        # Generate a random password with selected length by selecting characters from the set
        password = "".join(random.choice(characters) for _ in range(length))

        return password

    # ==================== VALIDATION ====================

    @api.constrains("phone")
    def _check_phone(self):
        """
        Check if the phone number is valid. Use regex to check if the phone number is in the correct format

        @params:
        1. self: Student object

        @return: validation error if phone number is invalid

        @decorator: api.constrains to call the function when creating or updating a Student object
        """

        _logger.info("PSM: Checking phone number")
        # Check if the phone number is valid
        # !TODO: Replace the regex with the correct phone number format for stronger validation
        pattern = r"^\d+$"
        for record in self:
            if record.phone and not re.match(pattern, record.phone):
                _logger.error("PSM: Invalid phone number: %s", record.phone)
                raise exceptions.ValidationError("Invalid phone number")

    @api.constrains("email")
    def _check_email(self):
        """
        Check if the email is valid. Use regex to check if the email is in the correct format

        @params:
        1. self: Student Object

        @return: validation error if email is invalid

        @decorator: api.constrains to call the function when creating or updating a Student object
        """

        _logger.info("PSM: Checking email")
        for record in self:
            # Check if the email is valid
            # Link Regex: https://regex101.com/r/O9oCj8/1
            if record.email and not re.match(
                r"^[^\.\s][\w\-\.{2,}]+@([\w-]+\.)+[\w-]{2,}$", record.email
            ):
                _logger.error("PSM: Invalid email: %s", record.email)
                raise exceptions.ValidationError("Invalid email")

    # ==================== OVERRIDE MODEL METHOD ====================

    def write(self, student_dict):
        """
        Update the student information.
        """

        # !TODO: Refresh student_list before update student

        _logger.info("PSM: Updating student")

        # Check if the email already exists in the database
        if "email" in student_dict:
            _logger.info("PSM: Checking email")
            if student_dict["email"] and self.env["portal.student"].search(
                [("email", "=", student_dict["email"])]
            ):
                _logger.error("PSM: Email already exists")
                _logger.debug("PSM: Email: %s", student_dict["email"])
                raise exceptions.ValidationError("Email already exists")
        return super(Student, self).write(student_dict)

    @api.model
    def create(self, student_dict):
        """
        Function is called when creating a new student. Validate email duplicate and create new student_code when creating a new one if it is duplicated.
        Check if student is created by import file or not by context, if not, send request to LMS API.

        @params:
            dict: student_dict: Student data sent from the form
            self: Student Object
        """

        _logger.info("PSM: Start to creating student")

        # !TODO: Refresh student_list before create new student
        student_dict["student_code"] = self._student_code_generator(
            student_dict
        )
        _logger.debug(
            "PSM: Assigned Student code: %s", student_dict["student_code"]
        )

        if student_dict["email"] and self.env["portal.student"].search(
            [("email", "=", student_dict["email"])]
        ):
            _logger.error("Email already exists")
            _logger.debug("Email: %s", student_dict["email"])
            raise exceptions.ValidationError("Email already exists")

        _logger.info("PSM: Checking phone number")
        self._check_phone()

        _logger.info("PSM: Checking if this is an import file")
        if not self.env.context.get(
            "import_file"
        ) and not self.env.context.get("from_lms"):
            _logger.info(
                "PSM: Not an import file or created from LMS, sending request to LMS"
            )

            headers = {
                "Content-Type": "application/json",
            }
            data_body = [
                {
                    "name": student_dict["name"],
                    "email": student_dict["email"],
                    "username": student_dict["username"],
                    "password": "Password1!",
                }
            ]

            _logger.debug("PSM: Data body create student: %s", data_body)

            response = self.send_api_request(
                data_body,
                headers,
                endpoint="api/funix_portal/user/create_user",
            )

            _logger.debug("PMS: Response create student: %s", response)

            # Check response status
            if (
                not response
                or response.status_code < 200
                or response.status_code >= 300
            ):
                _logger.error(
                    "PMS: Failed to create student in LMS: %s", response.text
                )
                raise exceptions.ValidationError(
                    "PMS: Failed to create student in LMS"
                )

        try:
            _logger.info("PSM: Creating student")
            new_student = super(Student, self).create(student_dict)
            _logger.info("PSM: Student created successfully")
            _logger.debug("PSM: New student: %s", new_student)
            return new_student
        except Exception as e:
            _logger.error("PSM: Failed to create student: %s", e)
            raise exceptions.ValidationError("Failed to create student")

    def send_api_request(self, data, headers, endpoint):
        """
        Function to send API request to LMS Staging

        @params:
        1. self: Student object
        2. data: Data to be sent
        3. headers: Headers to be sent
        """

        _logger.info("PMS: Sending request to LMS")

        base_url = self._extract_base_url()

        _logger.debug("PMS: Base URL: %s", base_url)

        # Define the URL Register API in LMS Staging
        url = f"{base_url}{endpoint}"

        _logger.debug("PMS: Full URL: %s", url)

        # Send the POST request
        try:
            _logger.info("PMS: Sending request")
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            _logger.debug("PMS: Response: %s", response)
            # Log the response
            _logger.info("PMS: Request sent successfully")

            return response
        except requests.RequestException as e:
            _logger.error(f"PMS: Failed to send request: {e}")
            return response

    @api.model
    def load(self, fields, data):
        """
        Function to load data from the import file, then send API request to LMS Staging
        Function will retrive context to check if it is an import test, if not, it will send API request

        @params:
        1. self: Student object
        2. fields: List of fields to be imported
        3. data: Data to be imported

        """
        _logger.info("PMS: Loading data from import file")

        # Perform the import operation
        result = super(Student, self).load(fields, data)

        # Check if the import was successful and if this is not a test import

        _logger.info("PMS: Checking if this is a test import")
        if result.get("ids") and not self.env.context.get("test_import"):
            # Fetch the data of the newly imported records
            _logger.info("PMS: Not a test import, sending request to LMS")

            _logger.info("PMS: Fetching newly imported records")
            imported_records = self.env["portal.student"].browse(result["ids"])
            _logger.debug("PMS: Imported records: %s", imported_records)

            # Prepare data for the API request
            headers = {
                "Content-Type": "application/json",
            }
            data_body = [
                {
                    "name": record.name,
                    "email": record.email,
                    "username": record.username,
                    "password": "Password1!",
                }
                for record in imported_records
            ]

            # Send the API request with all the data
            _logger.info("PMS: Sending request to LMS")
            response = self.send_api_request(
                data_body,
                headers,
                endpoint="api/funix_portal/user/create_user",
            )
            _logger.info("PMS: Request sent successfully")
            if (
                not response
                or response.status_code < 200
                or response.status_code >= 300
            ):
                _logger.error(
                    "PMS: Failed to import student in LMS: %s", response.text
                )
                _logger.debug("Response: %s", response)
                raise exceptions.ValidationError(
                    "PMS: Failed to import student in LMS"
                )

        return result

    def _extract_base_url(self):
        _logger.info("PMS: Extracting base URL")
        service_key_config = self.env["service_key_configuration"]

        _logger.debug("PMS: Service key config: %s", service_key_config)

        base_url = service_key_config.get_api_key_by_service_name("LMS_BASE")

        _logger.debug("PMS: Base URL: %s", base_url)
        _logger.info("PMS: Base URL extracted")
        return base_url

    def reset_password(self):
        """
        Function to call API to reset password
        """
        _logger.info("PMS: Resetting password")

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "email": self.email,
            "password": "Password1!",
            "new_password": "Password1!",
        }

        _logger.debug("PMS: Data body for reset password: %s", data)

        _logger.info("PMS: Sending request to LMS")
        response = self.send_api_request(
            data, headers, endpoint="api/funix_portal/user/update_password"
        )

        if response.status_code >= 200 and response.status_code < 300:
            _logger.info("PMS: Password reset successful")
            _logger.debug("PMS: Response success: %s", response)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Password reset successful",
                    "sticky": False,
                },
            }
        else:
            _logger.error("PMS: Password reset failed")
            _logger.debug("PMS: Response failed: %s", response)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Error",
                    "message": "Password reset failed",
                    "sticky": False,
                },
            }
