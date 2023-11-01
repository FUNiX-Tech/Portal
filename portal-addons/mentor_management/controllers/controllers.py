# -*- coding: utf-8 -*-
# from odoo import http


# class MentorManagement(http.Controller):
#     @http.route('/mentor_management/mentor_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mentor_management/mentor_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mentor_management.listing', {
#             'root': '/mentor_management/mentor_management',
#             'objects': http.request.env['mentor_management.mentor_management'].search([]),
#         })

#     @http.route('/mentor_management/mentor_management/objects/<model("mentor_management.mentor_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mentor_management.object', {
#             'object': obj
#         })
