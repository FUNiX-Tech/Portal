from odoo.http import request


def json_response(status=200, data=None):
    return request.make_json_response(status=status, data=data)
