import jwt
from datetime import datetime, timedelta
from werkzeug.exceptions import Unauthorized, BadRequest


class JWTEncoder:
    # SECRET_KEY AND ALGORITHM
    # !TODO: Replace the SECRET_KEY and ALGORITHM with appropriate values
    SECRET_KEY = "YOUR_SECRET_KEY"
    ALGORITHM = "HS256"

    @classmethod
    def encode_jwt(cls, payload, time_scale="minutes", time_expire=60):
        """
        Function to encode payload into token

        @params:
        1. cls: Class JWTEncoder, used to access variables in the class
        2. payload: Payload to be encoded
        3. time_scale: Time unit
            - days, seconds, minutes, hours, weeks, microseconds, milliseconds
        4. time_expire: Time to expire

        @return: encoded token

        """
        time_args = {time_scale: time_expire}
        payload["exp"] = datetime.now() + timedelta(**time_args)
        token = jwt.encode(payload, cls.SECRET_KEY, cls.ALGORITHM)
        return token

    @classmethod
    def decode_jwt(cls, token):
        """
        Function to decode token into payload

        @params:
        1. cls: Class JWTEncoder, used to access variables in the class
        2. token: Token to be decoded

        @return: decoded payload

        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, cls.ALGORITHM)
        except jwt.ExpiredSignatureError:
            raise Unauthorized("Access token expired")
        except jwt.InvalidTokenError:
            raise BadRequest("Access token invalid")
        except jwt.DecodeError:
            raise BadRequest("Access token invalid")
        return payload
