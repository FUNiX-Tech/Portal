import json
from odoo.http import Response


def json_response(status=200, message="success", data=None, metadata=None):
    response = {
        "data": data,
        "status": status,
        "message": message,
        "message": message,
        "metadata": metadata,
    }

    return Response(json.dumps(response), status=status)
