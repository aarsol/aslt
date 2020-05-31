import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class InvoiceRateWiz(models.TransientModel):
    _name = 'aslt.invoice.rate.wiz'
    _description = 'Invoice Rate Wiz'

    @api.model
    def _get_invoices(self):
        return self.env['res.partner'].browse(self._context.get('active_ids', False)).ids

    invoice_ids = fields.Many2many('account.move', string='Invoices',
        help="""Only selected Invoices will be Processed.""", default=_get_invoices)

    invoice_rate = fields.Selection([('low', 'Low Rate'), ('high', 'High Rate')], 'Invoice Rate', default='low')

    def set_rate(self):
        self.invoice_ids.update({'invoice_rate': self.invoice_rate})
        return {'type': 'ir.actions.act_window_close'}
