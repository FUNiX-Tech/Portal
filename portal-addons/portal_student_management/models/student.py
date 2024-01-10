# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
import random
import re
import string
import requests
import logging
import time

_logger = logging.getLogger(__name__)


class Student(models.Model):
    _name = "portal.student"
    _description = "Student Information"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    lms_created_status = fields.Boolean(
        string="LMS", default=False, readonly=True
    )
    udemy_created_status = fields.Boolean(
        string="Udemy", default=False, readonly=True
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
        student_code = student_dict.get("student_code")

        if not student_code:
            while True:
                # !TODO: Student code generator, need to change the algorithm to suit the needs
                # zfill(6) to fill 0 to reach 6 numbers => 000001, 000002, 000003,... -> string
                new_student_code = str(random.randint(1, 100000)).zfill(6)

                # Check if the student_code is already in the database
                if not self.env["portal.student"].search(
                    [("student_code", "=", new_student_code)]
                ):
                    student_code = new_student_code
                    break

        return student_code

    @api.model
    def _gender_generator(self, student_dict):
        gender = student_dict.get("gender")

        if not gender:
            gender = "unknown"

        return gender

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

        # Check if the phone number is valid
        # !TODO: Replace the regex with the correct phone number format for stronger validation
        pattern = r"^\d+$"
        for record in self:
            if record.phone and not re.match(pattern, record.phone):
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
        for record in self:
            # Check if the email is valid
            # Link Regex: https://regex101.com/r/O9oCj8/1
            if record.email and not re.match(
                r"^[^\.\s][\w\-\.{2,}]+@([\w-]+\.)+[\w-]{2,}$", record.email
            ):
                raise exceptions.ValidationError("Invalid email")

    # ==================== OVERRIDE MODEL METHOD ====================

    def write(self, student_dict):
        """
        Update the student information.
        """

        # !TODO: Refresh student_list before update student

        # Check if the email already exists in the database
        if "email" in student_dict:
            if student_dict["email"] and self.env["portal.student"].search(
                [("email", "=", student_dict["email"])]
            ):
                raise exceptions.ValidationError("Email already exists")
        return super(Student, self).write(student_dict)

    @api.model
    def create(self, vals):
        """
        Create a new student. If context 'from_lms' is not set, send an API request to LMS.
        Regardless of LMS, always send a request to Udemy. Implement retry mechanism for failed requests.
        """
        # Check for email duplication
        if "email" in vals and self.env["portal.student"].search(
            [("email", "=", vals["email"])]
        ):
            raise exceptions.ValidationError("Email already exists")

        # Set student_code and gender
        vals["student_code"] = self._student_code_generator(vals)
        vals["gender"] = self._gender_generator(vals)

        # Perform student creation in Odoo
        new_student = super(Student, self).create(vals)
        new_student.message_post(body="Student record created in Odoo.")

        # Send request to LMS unless 'from_lms' context is set
        if not self.env.context.get("from_lms"):
            lms_endpoint = "api/funix_portal/user/create_user"
            lms_success = self.send_api_request_to_platform(
                new_student, "LMS_BASE", lms_endpoint
            )

            # Retry mechanism for LMS request
            if lms_success == "retry":
                lms_success = self.retry_api_request(
                    new_student, "LMS_BASE", lms_endpoint
                )
            if lms_success == True:
                new_student.lms_created_status = True
                new_student.message_post(
                    body="Student successfully registered on LMS platform."
                )
            elif lms_success == False:
                new_student.message_post(
                    body="Failed to register student on LMS platform."
                )

        # Always send request to Udemy
        udemy_endpoint = "api/udemy/user/create_user"
        udemy_success = self.send_api_request_to_platform(
            new_student, "UDEMY_BASE", udemy_endpoint
        )

        # Retry mechanism for Udemy request
        if udemy_success == "retry":
            udemy_success = self.retry_api_request(
                new_student, "UDEMY_BASE", udemy_endpoint
            )

        if udemy_success == True:
            new_student.udemy_created_status = True
            self.action_send_email(
                new_student.email,
                email_cc="",
                body="Your Udemy account has been successfully created!",
                student_object=new_student,
            )
            new_student.message_post(
                body="Student successfully registered on Udemy platform."
            )
        elif udemy_success == False:
            self.action_send_email(
                new_student.email,
                email_cc="",
                body="Your Udemy account has failed to be created. Please contact support for assistance.",
                student_object=new_student,
            )
            new_student.message_post(
                body="Failed to register student on Udemy platform."
            )

        # Check both platforms' request results
        if not lms_success and not udemy_success:
            # Rollback Odoo student creation if both requests fail
            new_student.unlink()
            new_student.message_post(
                body="Student registration failed on both platforms. Record deleted from Odoo."
            )
            raise exceptions.ValidationError(
                "Failed to create student in external platforms"
            )

        return new_student

    def send_api_request_to_platform(self, student, base_url_name, endpoint):
        """
        Helper method to send an API request to a given platform.
        Returns True for success, 'retry' for 500 error, and False for other errors.
        """
        headers = {"Content-Type": "application/json"}
        data_body = [
            {
                "name": student.name,
                "email": student.email,
                "username": student.username,
                "password": "Password1!",
            }
        ]

        response = self.send_api_request(
            data_body, headers, base_url_name, endpoint
        )

        if response and 200 <= response.status_code < 300:
            return True
        elif response and response.status_code == 500:
            return "retry"
        else:
            return False

    def retry_api_request(self, student, base_url_name, endpoint):
        """
        Retry API request in case of a 500 error, up to 10 times with a 10-second interval.
        Does not retry for other error codes.
        """
        for attempt in range(10):
            time.sleep(10)
            response = self.send_api_request_to_platform(
                student, base_url_name, endpoint
            )
            self.message_post(body=f"Attempt {attempt+1}: {response}")
            if response is True:
                self.message_post(
                    body=f"Student successfully registered at attempt {attempt+1}."
                )
                return True
            elif response is not "retry":
                self.message_post(
                    body=f"Student registration failed at attempt {attempt+1}."
                )
                break

        self.action_send_email(
            student.email,
            email_cc="",
            body="Udemy registration failed after multiple attempts. Please contact support for assistance.",
            student_object=student,
        )
        self.message_post(
            body="Student registration failed after multiple attempts. Please contact support for assistance."
        )
        return False

    def send_api_request(self, data, headers, base_url_name, endpoint):
        """
        Function to send API request to LMS Staging

        @params:
        1. self: Student object
        2. data: Data to be sent
        3. headers: Headers to be sent
        """

        base_url = self._extract_base_url(base_url_name)

        # Define the URL Register API in LMS Staging
        url = f"{base_url}{endpoint}"

        print("urllllllllllllll", url)

        # Send the POST request
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # This will raise an error for HTTP error codes

            # Log the response
            _logger.info(f"Request sent successfully: {response.status_code}")

            return response
        except requests.RequestException as e:
            _logger.error(f"Failed to send request: {e}")
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
        # Perform the import operation
        result = super(Student, self).load(fields, data)

        # Check if the import was successful and if this is not a test import
        if result.get("ids") and not self.env.context.get("test_import"):
            # Fetch the data of the newly imported records
            imported_records = self.env["portal.student"].browse(result["ids"])

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
            response = self.send_api_request(
                data_body,
                headers,
                endpoint="api/funix_portal/user/create_user",
            )

            if (
                not response
                or response.status_code < 200
                or response.status_code >= 300
            ):
                raise exceptions.ValidationError(
                    "Failed to import student in LMS"
                )

        return result

    def _extract_base_url(self, base_url_name=None):
        service_key_config = self.env["service_key_configuration"]

        base_url = service_key_config.get_api_key_by_service_name(
            base_url_name
        )

        return base_url

    def reset_password(self):
        """
        Function to call API to reset password
        """

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "email": self.email,
            "password": "Password1!",
            "new_password": "Password1!",
        }

        response = self.send_api_request(
            data, headers, endpoint="api/funix_portal/user/update_password"
        )

        if response.status_code >= 200 and response.status_code < 300:
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
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Error",
                    "message": "Password reset failed",
                    "sticky": False,
                },
            }

    def call_send_email(
        self,
        recipient_email,
        email_cc,
        title,
        subject,
        body,
        description="Registration Status",
        external_link=False,
        external_text=False,
        ref_model="portal_student_management.model_portal_student",
        student_object=False,
        email_from="no-reply@funix.edu.vn",
    ):
        self.env["mail_service"].send_email_with_sendgrid(
            self.env["service_key_configuration"],
            recipient_email,
            email_cc,
            title,
            subject,
            body,
            description,
            external_link,
            external_text,
            ref_model,
            student_object,
            email_from,
        )

    def action_send_email(
        self,
        recipient_email,
        email_cc,
        student_object=False,
        body="",
    ):
        self.call_send_email(
            recipient_email,
            email_cc,
            title="Funix Portal Registration",
            subject="Funix Portal Registration Status",
            body=body,
            description="Registration Status",
            external_link=False,
            external_text=False,
            ref_model="portal_student_management.model_portal_student",
            student_object=student_object,
            email_from="no-reply@funix.edu.vn",
        )
        # Ensure message_post is called on a valid single record
        if student_object:
            student_object.message_post(
                body=f"Email sent to {recipient_email}: {body}"
            )
