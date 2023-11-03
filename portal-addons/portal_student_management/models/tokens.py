from odoo import fields, models
import uuid


def unique_constraint(message):
    return ("student_id_unique", "UNIQUIE(student_id)", message)


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


# ==================== ONE-TIME TOKENS: WILL BE CLEANED ====================
class StudentEmailVerificationToken(models.TransientModel):
    _name = "portal.student.email.verification.token"
    _description = "Token for student email verification"
    student_id = fields.Many2one(
        "portal.student", string="Student", required=True, ondelete="cascade"
    )
    token = fields.Char(string="Email verification token")
    expired_at = fields.Datetime(string="Expired at")
    created_at = fields.Datetime(
        string="Created At", readonly=True, default=fields.Datetime.now()
    )
    used = fields.Boolean(string="Used", default=False)

    _sql_constraints = [

        unique_constraint(
            "Each student can only create one email verification token"
        )
    ]

    def create_verification_token(self, student_id):
        student = (
            self.env["portal.student"].sudo().search([("id", "=", student_id)])
        )

        if student:
            token = self.generate_token()
            return self.create(
                {
                    "student_id": student.id,
                    "token": token,
                }
            )
        return False


class StudentPasswordResetToken(models.TransientModel):
    _name = "portal.student.password.reset.token"
    _description = "Token for student password reset"
    student_id = fields.Many2one(
        "portal.student", string="Student", required=True, ondelete="cascade"
    )
    token = fields.Char(string="Password reset token")
    expired_at = fields.Datetime(string="Expired at")
    used = fields.Boolean(string="Used", default=False)

    _sql_constraints = [

        unique_constraint(
            "Each student can only create one password reset token"
        )
    ]


# ==================== REFRESH TOKEN: WILL GENERATE AFTER SUCCESSFUL LOGIN ====================


class StudentRefreshToken(models.Model):
    _name = "portal.student.refresh.token"
    _description = "Refresh token of student"

    student_id = fields.Many2one(
        "portal.student", string="Student", required=True, ondelete="cascade"
    )
    token = fields.Char(string="Token refresh")
    expired_at = fields.Datetime(string="Expired at")
    used = fields.Boolean(string="Used", default=False)

    _sql_constraints = [
        unique_constraint("Each student can only create one refresh token")
    ]
