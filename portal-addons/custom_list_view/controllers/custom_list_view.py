from odoo import http
from odoo.http import request


class ExportData(http.Controller):
    """Controller class for exporting data from Odoo models."""

    @http.route("/get-data", auth="user", type="json")
    def get_export_data_pdf(self, **kw):
        # Example: model = portal.student, payload from list_controller.js
        model = request.env[kw["model"]]
        field_names = []
        columns_headers = []

        for field in kw["fields"]:
            field_names.append(
                field["name"]
            )  # Extracting field names: student_code, email,...
            columns_headers.append(
                field["label"].strip()
            )  # Extracting field labels: Student code, Email,...

        # If res_ids passed from list_controller is not empty, get records based on res_ids. Else get records based on domain
        if kw["res_ids"]:
            domain = [("id", "in", kw["res_ids"])]
            records = model.browse(
                kw["res.ids"]
            )  # Get records based on res_ids
        else:
            domain = kw["domain"]
            records = model.search(domain)  # Get records based on domain

        # Utilize built-in Odoo export_data method from model.Models to export data
        export_data = records.export_data(field_names).get("datas", [])
        return {"data": export_data, "header": columns_headers}

    @http.route("/get-data/copy", auth="user", type="json")
    def get_export_data_for_copy(self, **kw):
        # Example: model = portal.student, payload from list_controller.js
        model = request.env[kw["model"]]
        field_names = []
        columns_headers = []

        for field in kw["fields"]:
            field_names.append(
                field["name"]
            )  # Extracting field names: student_code, email,...
            columns_headers.append(
                field["label"].strip()
            )  # Extracting field labels: Student code, Email,...

        # If res_ids passed from list_controller is not empty, get records based on res_ids. Else get records based on domain
        if kw["res_ids"]:
            domain = [("id", "in", kw["res_ids"])]
            records = model.browse(
                kw["res.ids"]
            )  # Get records based on res_ids
        else:
            domain = kw["domain"]
            records = model.search(domain)  # Get records based on domain

        # Utilize built-in Odoo export_data method from model.Models to export data
        export_data = records.export_data(field_names).get("datas", [])
        export_data.insert(0, columns_headers)  # Insert column headers
        return export_data
