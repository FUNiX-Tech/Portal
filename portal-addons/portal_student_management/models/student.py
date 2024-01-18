# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
import random
import re
import string
import requests
import logging
import time

_logger = logging.getLogger(__name__)

UDEMY_BASE_CONFIG = "UDEMY_BASE"
LMS_BASE_CONFIG = "LMS_BASE"
UDEMY_ENDPOINT = "api/udemy/user/create_user"
LMS_ENDPOINT = "api/funix_portal/user/create_user"


class Student(models.Model):
    _name = "portal.student"
    _description = "Student Information"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Char(string="Student Name", required=True)
    username = fields.Char(string="Username", required=True, unique=True)
    email = fields.Char(string="Email", required=True, unique=True, index=True)
    student_code = fields.Char(string="Student Code")
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

    def _call_send_email(
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
        _logger.info("Checking phone number")
        # Check if the phone number is valid
        # !TODO: Replace the regex with the correct phone number format for stronger validation
        pattern = r"^\d+$"
        for record in self:
            if record.phone and not re.match(pattern, record.phone):
                _logger.error("Invalid phone number")
                raise exceptions.ValidationError("Invalid phone number")

    @api.constrains("email")
    def _check_email(self):
        _logger.info("Checking email")
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
                _logger.error("Invalid email")
                raise exceptions.ValidationError("Invalid email")

    def _handle_lms_registration(self, student):
        _logger.info("Registering student on LMS platform")
        lms_registration_status = False
        lms_payload = self._prepare_lms_payload(student)
        _logger.debug(f"LMS payload: {lms_payload}")
        if not self.env.context.get("from_lms"):
            _logger.info("Student is created from Portal")
            lms_registration_status = self._send_api_request_to_platform(
                lms_payload, LMS_BASE_CONFIG, LMS_ENDPOINT
            )

            _logger.debug(
                f"LMS registration status: {lms_registration_status}"
            )
            # Retry mechanism for LMS request
            if lms_registration_status == "retry":
                lms_registration_status = self._retry_api_request(
                    lms_payload, LMS_BASE_CONFIG, LMS_ENDPOINT
                )
                _logger.info("Something went wrong. Retrying LMS request")
                _logger.debug(
                    f"LMS registration status after retry: {lms_registration_status}"
                )
            if lms_registration_status is True:
                student.lms_created_status = True
                student.message_post(
                    body="Student successfully registered on LMS platform."
                )
            elif lms_registration_status is False:
                student.message_post(
                    body="Failed to register student on LMS platform."
                )

        print("lms_registration_status", lms_registration_status)
        return lms_registration_status

    def _handle_udemy_registration(self, student):
        _logger.info("Registering student on Udemy platform")
        udemy_registration_status = False
        udemy_payload = self._prepare_udemy_payload(student)

        # Always send request to Udemy
        udemy_registration_status = self._send_api_request_to_platform(
            udemy_payload, UDEMY_BASE_CONFIG, UDEMY_ENDPOINT
        )

        _logger.debug(
            f"Udemy registration status: {udemy_registration_status}"
        )

        # Retry mechanism for Udemy request
        if udemy_registration_status == "retry":
            udemy_registration_status = self._retry_api_request(
                student, udemy_payload, UDEMY_BASE_CONFIG, UDEMY_ENDPOINT
            )
            _logger.info("Something went wrong. Retrying Udemy request")
            _logger.debug(
                f"Udemy registration status after retry: {udemy_registration_status}"
            )

        if udemy_registration_status is True:
            student.udemy_created_status = True
            self.action_send_email(
                student.email,
                email_cc="",
                body="Your Udemy account has been successfully created!",
                student_object=student,
            )
            student.message_post(
                body="Student successfully registered on Udemy platform."
            )
        elif udemy_registration_status is False:
            self.action_send_email(
                student.email,
                email_cc="",
                body="Your Udemy account has failed to be created. Please contact support for assistance.",
                student_object=student,
            )
            student.message_post(
                body="Failed to register student on Udemy platform."
            )

        return udemy_registration_status

    def _prepare_udemy_payload(self, student):
        _logger.info("Preparing Udemy payload")
        udemy_data_body = {
            "name": student.name,
            "email": student.email,
            "username": student.username,
            "password": "Password1!",
        }
        _logger.debug(f"Udemy payload: {udemy_data_body}")

        return udemy_data_body

    def _prepare_lms_payload(self, student):
        _logger.info("Preparing LMS payload")
        lms_data_body = {
            "name": student.name,
            "email": student.email,
            "username": student.username,
            "password": "Password1!",
        }
        _logger.debug(f"LMS payload: {lms_data_body}")

        return lms_data_body

    def _registration_response_checker(self, response, base_url_name):
        if 200 <= response.status_code < 300:
            _logger.debug(
                f"This is a {response.status_code} response, returning True for {base_url_name}"
            )
            return True
        elif response.status_code == 500:
            _logger.debug(
                f"This is a {response.status_code} response, returning retry for {base_url_name}"
            )
            return "retry"
        elif response.status_code < 200 or response.status_code >= 300:
            _logger.debug(
                f"This is a {response.status_code} response, returning False for {base_url_name}"
            )
            return False

    def _extract_base_url(self, base_url_name=None):
        _logger.info(f"Extracting base url for {base_url_name}")
        service_key_config = self.env["service_key_configuration"]

        base_url = service_key_config.get_api_key_by_service_name(
            base_url_name
        )
        _logger.debug(f"Base url: {base_url}")

        return base_url

    def _send_api_request_to_platform(
        self, data_body, base_url_name, endpoint
    ):
        """
        Helper method to send an API request to a given platform.
        Returns True for success, 'retry' for 500 error, and False for other errors.
        """
        _logger.info(f"Sending API request to {base_url_name}")
        headers = {"Content-Type": "application/json"}

        response = self._send_api_request(
            data_body, headers, base_url_name, endpoint
        )

        _logger.debug(f"Response: {response}")

        response_checker = self._registration_response_checker(
            response, base_url_name
        )

        return response_checker

    def _retry_api_request(self, student, data_body, base_url_name, endpoint):
        """
        Retry API request in case of a 500 error, up to 10 times with a 10-second interval.
        Does not retry for other error codes.
        """

        _logger.info(f"Retrying API request to {base_url_name}")

        for attempt in range(10):
            time.sleep(10)
            response = self._send_api_request_to_platform(
                data_body, base_url_name, endpoint
            )
            _logger.debug(f"Response at attempt {attempt+1}: {response}")
            self.message_notify(body=f"Attempt {attempt+1}: {response}")
            if response is True:
                self.message_notify(
                    body=f"{student.name} successfully registered at attempt {attempt+1}."
                )
                return True
            elif response != "retry":
                self.message_notify(
                    body=f"{student.name} registration failed at attempt {attempt+1}."
                )
                break

        # self.action_send_email(
        #     student.email,
        #     email_cc="",
        #     body=f"{student.name} registration failed at {base_url_name} after multiple attempts. Please contact support for assistance.",
        #     student_object=student,
        # )

        _logger.info(
            f"Failed to register {student.name} at {base_url_name} after multiple attempts"
        )

        self.message_notify(
            body=f"{student.name} registration failed at {base_url_name} after multiple attempts. Please contact support for assistance."
        )
        return False

    def _send_api_request(self, data, headers, base_url_name, endpoint):
        """
        Function to send API request to LMS Staging

        @params:
        1. self: Student object
        2. data: Data to be sent
        3. headers: Headers to be sent
        """

        _logger.info(f"Sending API request to {base_url_name}")

        base_url = self._extract_base_url(base_url_name)

        # Define the URL Register API in LMS Staging
        url = f"{base_url}{endpoint}"

        _logger.debug("URL: " + url)
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
        _logger.info("Creating new student")
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

        if not self.env.context.get("test_import"):
            new_student.message_post(body="Student record created in Odoo.")
            _logger.info("New student created in Odoo")
            _logger.debug(f"New student: {new_student}")

            lms_registration_status = self._handle_lms_registration(
                new_student
            )
            _logger.debug(
                f"Final LMS registration status: {lms_registration_status}"
            )

            # Check both platforms' request results
            if lms_registration_status == "False":
                # Rollback Odoo student creation if both requests fail
                new_student.unlink()
                _logger.info(
                    "LMS platform failed to register student. Rollback Odoo student creation"
                )
                new_student.message_post(
                    body="Student registration failed on LMS platform. Record deleted from Odoo."
                )
                raise exceptions.ValidationError(
                    "Failed to create student in LMS platform"
                )
            else:
                udemy_registration_status = self._handle_udemy_registration(
                    new_student
                )
                _logger.debug(
                    f"Final Udemy registration status: {udemy_registration_status}"
                )

        return new_student

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
        _logger.info("Loading data from import file")
        # Perform the import operation
        result = super(Student, self).load(fields, data)

        # Check if the import was successful and if this is not a test import
        # if result.get("ids") and not self.env.context.get("test_import"):
        #     # Fetch the data of the newly imported records
        #     imported_records = self.env["portal.student"].browse(result["ids"])

        #     # Prepare data for the API request
        #     headers = {
        #         "Content-Type": "application/json",
        #     }
        #     data_body = [
        #         {
        #             "name": record.name,
        #             "email": record.email,
        #             "username": record.username,
        #             "password": "Password1!",
        #         }
        #         for record in imported_records
        #     ]

        #     # Send the API request with all the data
        #     response = self._send_api_request(
        #         data_body,
        #         headers,
        #         LMS_BASE_CONFIG,
        #         LMS_ENDPOINT
        #     )

        #     if (
        #         not response
        #         or response.status_code < 200
        #         or response.status_code >= 300
        #     ):
        #         raise exceptions.ValidationError(
        #             "Failed to import student in LMS"
        #         )

        return result

    def reset_password(self):
        """
        Function to call API to reset password
        """

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "email": self.email,
            "new_password": "NewPassword1!",
        }

        response = self._send_api_request(
            data,
            headers,
            LMS_BASE_CONFIG,
            endpoint="api/v2/funix_portal/user/update_password",
        )

        if response.status_code >= 200 and response.status_code < 300:
            self.action_send_email(
                self.email,
                email_cc="",
                body=f"This is your new password: {data['new_password']}",
                student_object=self,
            )

            self.message_post(
                body=f"Password reset successful for {self.name}."
            )
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
            self.message_post(body=f"Password reset failed for {self.name}.")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Error",
                    "message": "Password reset failed",
                    "sticky": False,
                },
            }

    # ==================== Actions ====================

    def action_send_email(
        self,
        recipient_email,
        email_cc,
        student_object=False,
        body="",
    ):
        self._call_send_email(
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

    def action_register_in_lms(self):
        self._handle_lms_registration(self)

    def action_register_in_udemy(self):
        self._handle_udemy_registration(self)
