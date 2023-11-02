# -*- coding: utf-8 -*-
# from odoo import http


# class Feedback-ticket-management(http.Controller):
#     @http.route('/feedback-ticket-management/feedback-ticket-management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/feedback-ticket-management/feedback-ticket-management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('feedback-ticket-management.listing', {
#             'root': '/feedback-ticket-management/feedback-ticket-management',
#             'objects': http.request.env['feedback-ticket-management.feedback-ticket-management'].search([]),
#         })

#     @http.route('/feedback-ticket-management/feedback-ticket-management/objects/<model("feedback-ticket-management.feedback-ticket-management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('feedback-ticket-management.object', {
#             'object': obj
#         })
