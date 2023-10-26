from odoo import api, fields, models, exceptions

import uuid


def unique_constraint(message):
    return ('student_id_unique', 'UNIQUIE(student_id)', message)


def generate_token(self, length=32):
    """
    Hàm để tạo token cho reset mật khẩu, xác thực email

    @params:
    1. self: Đối tượng Token
    2. length: Độ dài token

    @return: token được tạo

    """
    token = uuid.uuid4().hex
    while len(token) < length:
        token += uuid.uuid4().hex
    return token[:length]


# ==================== ONE-TIME TOKENS: WILL BE CLEANED ====================
class StudentEmailVerificationToken(models.TransientModel):
    _name = "portal.student.email.verification.token"
    _description = "Token xác thực email học viên"
    student_id = fields.Many2one(
        'portal.student', string='Học viên', required=True, ondelete='cascade')
    token = fields.Char(string='Token xác thực email')
    expired_at = fields.Datetime(string='Hết hạn')
    created_at = fields.Datetime(
        string='Ngày tạo', readonly=True, default=fields.Datetime.now())
    used = fields.Boolean(string='Đã sử dụng', default=False)

    _sql_constraints = [
        unique_constraint('Mỗi học viên chỉ được tạo một token xác thực email')
    ]

    def create_verification_token(self, student_id):
        student = self.env['portal.student'].sudo().search(
            [('id', '=', student_id)])

        if student:
            token = self.generate_token()
            return self.create({
                'student_id': student.id,
                'token': token,
            })
        return False


class StudentPasswordResetToken(models.TransientModel):
    _name = "portal.student.password.reset.token"
    _description = "Token reset mật khẩu học viên"
    student_id = fields.Many2one(
        'portal.student', string='Học viên', required=True, ondelete='cascade')
    token = fields.Char(string='Token reset mật khẩu')
    expired_at = fields.Datetime(string='Hết hạn')
    used = fields.Boolean(string='Đã sử dụng', default=False)

    _sql_constraints = [
        unique_constraint('Mỗi học viên chỉ được tạo một token reset mật khẩu')
    ]


# ==================== REFRESH TOKEN: WILL GENERATE AFTER SUCCESSFUL LOGIN ====================

class StudentRefreshToken(models.Model):
    _name = "portal.student.refresh.token"
    _description = "Token refresh học viên"

    student_id = fields.Many2one(
        'portal.student', string='Học viên', required=True, ondelete='cascade')
    token = fields.Char(string='Token refresh')
    expired_at = fields.Datetime(string='Hết hạn')
    used = fields.Boolean(string='Đã sử dụng', default=False)

    _sql_constraints = [
        unique_constraint('Mỗi học viên chỉ được tạo một token refresh')
    ]
