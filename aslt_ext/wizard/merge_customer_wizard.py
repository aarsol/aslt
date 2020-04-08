import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class CustomerMergeWiz(models.TransientModel):
    _name = 'aslt.customer.merge.wiz'
    _description = 'Customer Merge Wiz'

    @api.model
    def _get_customer(self):
        customer_id = self.env['res.partner'].browse(self._context.get('active_id', False))
        if customer_id:
            return customer_id.id

    customer_id = fields.Many2one('res.partner', string='Customer',
                                  help="""Only select Customer will be Processed.""", default=_get_customer)

    merge_customer_id = fields.Many2one('res.partner', string='Merge Customer With',
                                        help="""Only select Customer will be Processed.""", )

    def merge_customer(self):
        for rec in self:
            pdb.set_trace()

            sale_search = self.env['sale.order'].search([('partner_id', '=', rec.customer_id.id)])
            purchase_search = self.env['purchase.order'].search([('partner_id', '=', rec.customer_id.id)])
            account_move_search = self.env['account.move'].search([('partner_id', '=', rec.customer_id.id)])
            account_payment_search = self.env['account.payment'].search([('partner_id', '=', rec.customer_id.id)])
            for sale in sale_search:
                sale_line = self.env['sale.order.line'].search([('order_id', '=', sale.id)])
                for line in sale_line:
                    line.update({'order_partner_id': rec.merge_customer_id.id})
                sale.update({'partner_id': rec.merge_customer_id.id})
            for purchase in purchase_search:
                purchase_line = self.env['purchase.order.line'].search([('order_id', '=', purchase.id)])
                for line in sale_line:
                    line.update({'partner_id': rec.merge_customer_id.id})
                purchase.update({'partner_id': rec.merge_customer_id.id})
            for move in account_move_search:
                move_line = self.env['account.move.line'].search([('move_id', '=', move.id)])
                for line in move_line:
                    line.update({'partner_id': rec.merge_customer_id.id})
                move.update({'partner_id': rec.merge_customer_id.id})

            for payment in account_payment_search:
                payment.update({'partner_id': rec.merge_customer_id.id})

            rec.customer_id.unlink()

        return {'type': 'ir.actions.act_window_close'}
