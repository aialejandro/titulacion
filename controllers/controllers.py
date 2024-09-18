# -*- coding: utf-8 -*-
# from odoo import http


# class MlLearning(http.Controller):
#     @http.route('/ml_learning/ml_learning', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ml_learning/ml_learning/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ml_learning.listing', {
#             'root': '/ml_learning/ml_learning',
#             'objects': http.request.env['ml_learning.ml_learning'].search([]),
#         })

#     @http.route('/ml_learning/ml_learning/objects/<model("ml_learning.ml_learning"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ml_learning.object', {
#             'object': obj
#         })
