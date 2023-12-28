import json
from odoo.http import Response


def json_response(status=200, message="success", data=None, metadata=None):
    response = {
        "data": data,
        "status": status,
        "message": message,
        "metadata": metadata,
    }

    http_response = Response(json.dumps(response), status=status)

    http_response.headers.add("Access-Control-Allow-Credentials", "true")

    return http_response

    # return Response(json.dumps(response), status=status)
