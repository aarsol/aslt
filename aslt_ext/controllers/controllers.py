# -*- coding: utf-8 -*-
# from odoo import http


# class AsltExt(http.Controller):
#     @http.route('/aslt_ext/aslt_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aslt_ext/aslt_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aslt_ext.listing', {
#             'root': '/aslt_ext/aslt_ext',
#             'objects': http.request.env['aslt_ext.aslt_ext'].search([]),
#         })

#     @http.route('/aslt_ext/aslt_ext/objects/<model("aslt_ext.aslt_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aslt_ext.object', {
#             'object': obj
#         })
