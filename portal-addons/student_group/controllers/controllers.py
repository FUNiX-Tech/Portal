# -*- coding: utf-8 -*-
# from odoo import http


# class StudentGroup(http.Controller):
#     @http.route('/student_group/student_group', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/student_group/student_group/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('student_group.listing', {
#             'root': '/student_group/student_group',
#             'objects': http.request.env['student_group.student_group'].search([]),
#         })

#     @http.route('/student_group/student_group/objects/<model("student_group.student_group"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('student_group.object', {
#             'object': obj
#         })
