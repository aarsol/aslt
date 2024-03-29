# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class purchase_order(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def default_get(self, default_fields):
        res = super(purchase_order, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({'branch_id': branch_id})
        return res

    branch_id = fields.Many2one('res.branch', string="Branch")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrder, self).default_get(fields)
        branch_id = picking_type_id = False

        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        res.update({
            'branch_id': branch_id,
        })

        return res

    branch_id = fields.Many2one('res.branch', string='Branch')

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''

        result = super(PurchaseOrder, self).action_view_invoice()

        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        if 'context' in result:
            result['context'].update({
                'default_branch_id': branch_id,
                'branch_id': branch_id
            })

        return result


class StockPicking(models.Model):
    _inherit = "stock.picking"

    branch_id = fields.Many2one(string="Branch", related="purchase_id.branch_id")
