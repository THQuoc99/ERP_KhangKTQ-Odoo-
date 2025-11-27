# -*- coding: utf-8 -*-
# from odoo import http


# class KtqGhtkIntegration(http.Controller):
#     @http.route('/ktq_ghtk_integration/ktq_ghtk_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ktq_ghtk_integration/ktq_ghtk_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ktq_ghtk_integration.listing', {
#             'root': '/ktq_ghtk_integration/ktq_ghtk_integration',
#             'objects': http.request.env['ktq_ghtk_integration.ktq_ghtk_integration'].search([]),
#         })

#     @http.route('/ktq_ghtk_integration/ktq_ghtk_integration/objects/<model("ktq_ghtk_integration.ktq_ghtk_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ktq_ghtk_integration.object', {
#             'object': obj
#         })

