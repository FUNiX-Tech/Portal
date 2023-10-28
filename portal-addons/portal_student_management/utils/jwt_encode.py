import jwt
from datetime import datetime, timedelta
from werkzeug.exceptions import Unauthorized, BadRequest


class JWTEncoder:

    # SECRET_KEY AND ALGORITHM
    # !TODO: Thay đổi SECRET_KEY và ALGORITHM phù hợp với nhu cầu. Thay thế bằng env variable
    SECRET_KEY = 'YOUR_SECRET_KEY'
    ALGORITHM = 'HS256'

    @classmethod
    def encode_jwt(cls, payload, time_scale='minutes', time_expire=60):
        """
        Hàm để mã hóa payload thành token

        @params:
        1. cls: Class JWTEncoder, dùng để truy cập các biến trong class
        2. payload: Dữ liệu cần mã hóa
        3. time_scale: Đơn vị thời gian
            - days, seconds, minutes, hours, weeks, microseconds, milliseconds
        4. time_expire: Số lượng đơn vị thời gian

        @return: token được mã hóa

        """
        time_args = {time_scale: time_expire}
        payload['exp'] = datetime.now() + timedelta(**time_args)
        token = jwt.encode(payload, cls.SECRET_KEY, cls.ALGORITHM)
        return token

    @classmethod
    def decode_jwt(cls, token):
        """
        Hàm để giải mã token thành payload

        @params:
        1. cls: Class JWTEncoder, dùng để truy cập các biến trong class
        2. token: Token cần giải mã

        @return: payload được giải mã

        """
        payload = jwt.decode(token, cls.SECRET_KEY, cls.ALGORITHM)
        return payload
