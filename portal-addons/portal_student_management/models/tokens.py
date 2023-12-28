from odoo import fields, models
import uuid


def unique_constraint(message):
    return ("student_id_unique", "UNIQUE(student_id)", message)


def generate_token(self, length=32):
    """
    Function to create token for password reset, email verification

    @params:
    1. self: Token object
    2. length: length of the token

    @return: Created token

    """
    token = uuid.uuid4().hex
    while len(token) < length:
        token += uuid.uuid4().hex
    return token[:length]
