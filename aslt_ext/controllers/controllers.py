# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class AsltExt(http.Controller):
    @http.route('/aslt_ext/invoice_move/<int:id>', type='http', auth="public", website=True)
    def accept(self,id=0, **kw):

        invoice = http.request.env['account.move'].sudo().search([('id','=',id)])
        if invoice.marked_user_id and invoice.marked_state == 'draft':
            invoice.update({'marked_state':'accept'})
            values = {
                'header': 'Action Done Successfully  !',
                'message': 'Your Action is Accept Successfully.\n Thank you.'
            }
            return request.render("aslt_ext.portal_submission_message", values)
        else:
            values = {
                'header': 'Duplicate Error!',
                'message': 'Your Action is already been entertained! You can check on view .\n Thank you.'
            }
            return request.render("aslt_ext.portal_submission_message", values)


    @http.route('/aslt_ext/invoice_move_reject/<int:id>', auth='public')
    def reject(self, id=0, **kw):

        invoice = http.request.env['account.move'].sudo().search([('id', '=', id)])
        if invoice.marked_user_id and invoice.marked_state == 'draft':
            invoice.update({'marked_state': 'cancel'})
            values = {
                'header': 'Action Done Successfully  !',
                'message': 'Your Action is cancel Successfully.\n Thank you.'
            }
            return request.render("aslt_ext.portal_submission_message", values)
        else:
            values = {
                'header': 'Duplicate Error!',
                'message': 'Your Action is already been entertained! You can check on view .\n Thank you.'
            }
            return request.render("aslt_ext.portal_submission_message", values)


    # @http.route('/aslt_ext/aslt_ext/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('aslt_ext.listing', {
    #         'root': '/aslt_ext/aslt_ext',
    #         'objects': http.request.env['aslt_ext.aslt_ext'].search([]),
    #     })
    #
    # @http.route('/aslt_ext/aslt_ext/objects/<model("aslt_ext.aslt_ext"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('aslt_ext.object', {
    #         'object': obj
    #     })
